"""
Data export tasks for Hospital Management System.
"""
import logging
import csv
import io
import os
import uuid
from datetime import datetime, timedelta
from celery import shared_task

from backend.celery_app import celery
from backend.app.models import db, Patient, Appointment, Treatment
from backend.app.services.notification_service import notification_service

logger = logging.getLogger(__name__)

# Export storage directory
EXPORT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'exports')

# In-memory export status storage (in production, use Redis)
export_status = {}


def ensure_export_dir():
    """Ensure the export directory exists."""
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def export_patient_history_csv(self, patient_id, notify=True):
    """
    Export patient's treatment history to CSV.

    Args:
        patient_id: ID of the patient
        notify: Whether to send notification when complete

    Returns:
        dict with export status and file info
    """
    task_id = self.request.id
    export_status[task_id] = {
        'status': 'processing',
        'progress': 0,
        'started_at': datetime.utcnow().isoformat()
    }

    try:
        from backend.app import create_app
        app = create_app()

        with app.app_context():
            patient = Patient.query.get(patient_id)

            if not patient:
                export_status[task_id] = {
                    'status': 'failed',
                    'error': 'Patient not found',
                    'completed_at': datetime.utcnow().isoformat()
                }
                return {'success': False, 'message': 'Patient not found'}

            export_status[task_id]['progress'] = 10

            # Get all appointments with treatments
            appointments = Appointment.query.filter(
                Appointment.patient_id == patient_id
            ).order_by(Appointment.appointment_date.desc()).all()

            export_status[task_id]['progress'] = 30

            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow([
                'User ID',
                'Username',
                'Patient Name',
                'Consulting Doctor',
                'Department',
                'Appointment Date',
                'Appointment Time',
                'Status',
                'Visit Type',
                'Diagnosis',
                'Prescription',
                'Tests Recommended',
                'Notes',
                'Follow-up Date'
            ])

            export_status[task_id]['progress'] = 50

            # Write appointment data
            for apt in appointments:
                treatment = Treatment.query.filter_by(appointment_id=apt.id).first()
                doctor = apt.doctor

                writer.writerow([
                    patient.user.id if patient.user else '',
                    patient.user.username if patient.user else '',
                    patient.full_name,
                    doctor.full_name if doctor else 'N/A',
                    doctor.department.name if doctor and doctor.department else 'N/A',
                    apt.appointment_date.strftime('%Y-%m-%d'),
                    apt.appointment_time.strftime('%H:%M'),
                    apt.status,
                    treatment.visit_type if treatment else 'N/A',
                    treatment.diagnosis if treatment else 'N/A',
                    treatment.prescription if treatment else 'N/A',
                    treatment.tests_recommended if treatment else 'N/A',
                    treatment.notes if treatment else 'N/A',
                    treatment.follow_up_date.strftime('%Y-%m-%d') if treatment and treatment.follow_up_date else 'N/A'
                ])

            export_status[task_id]['progress'] = 80

            # Save to file
            ensure_export_dir()
            file_id = str(uuid.uuid4())
            filename = f"patient_{patient_id}_history_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(EXPORT_DIR, f"{file_id}_{filename}")

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                f.write(output.getvalue())

            export_status[task_id]['progress'] = 90

            # Update status
            export_status[task_id] = {
                'status': 'completed',
                'progress': 100,
                'file_id': file_id,
                'filename': filename,
                'filepath': filepath,
                'row_count': len(appointments),
                'completed_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
            }

            # Notify patient if requested
            if notify and patient.user:
                download_url = f"/api/patient/download-export/{file_id}"
                notification_service.send_export_ready(
                    patient_email=patient.user.email,
                    patient_name=patient.full_name,
                    download_url=download_url
                )

            logger.info(f"Export completed for patient {patient_id}: {filename}")
            return {
                'success': True,
                'file_id': file_id,
                'filename': filename,
                'row_count': len(appointments)
            }

    except Exception as e:
        logger.error(f"Error exporting patient history {patient_id}: {e}")
        export_status[task_id] = {
            'status': 'failed',
            'error': str(e),
            'completed_at': datetime.utcnow().isoformat()
        }
        raise self.retry(exc=e)


def get_export_status(task_id):
    """
    Get the status of an export task.

    Args:
        task_id: Celery task ID

    Returns:
        dict with export status
    """
    if task_id in export_status:
        return export_status[task_id]

    # Check Celery result backend
    from backend.celery_app import celery
    result = celery.AsyncResult(task_id)

    if result.state == 'PENDING':
        return {'status': 'pending', 'progress': 0}
    elif result.state == 'STARTED':
        return {'status': 'processing', 'progress': 0}
    elif result.state == 'SUCCESS':
        return {'status': 'completed', 'result': result.result}
    elif result.state == 'FAILURE':
        return {'status': 'failed', 'error': str(result.result)}
    else:
        return {'status': result.state}


def get_export_file(file_id):
    """
    Get export file by ID.

    Args:
        file_id: Export file ID

    Returns:
        tuple (filepath, filename) or None if not found
    """
    ensure_export_dir()

    # Find file matching the ID
    for filename in os.listdir(EXPORT_DIR):
        if filename.startswith(file_id):
            filepath = os.path.join(EXPORT_DIR, filename)
            # Extract original filename (after the UUID_)
            original_filename = filename[len(file_id) + 1:]
            return filepath, original_filename

    return None, None


def cleanup_old_exports(max_age_hours=24):
    """
    Clean up export files older than max_age_hours.

    Args:
        max_age_hours: Maximum age in hours

    Returns:
        Number of files deleted
    """
    ensure_export_dir()
    deleted = 0
    cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)

    for filename in os.listdir(EXPORT_DIR):
        filepath = os.path.join(EXPORT_DIR, filename)
        if os.path.isfile(filepath):
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_time < cutoff:
                os.remove(filepath)
                deleted += 1
                logger.info(f"Deleted old export: {filename}")

    return deleted


@celery.task
def cleanup_exports_task():
    """Periodic task to clean up old export files."""
    deleted = cleanup_old_exports(24)
    logger.info(f"Export cleanup completed: {deleted} files deleted")
    return {'deleted': deleted}
