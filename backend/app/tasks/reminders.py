"""
Appointment reminder tasks for Hospital Management System.
"""
import logging
from datetime import datetime, date
from celery import shared_task

from backend.celery_app import celery
from backend.app.models import db, Appointment, Patient, Doctor
from backend.app.services.notification_service import notification_service

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=300)
def send_daily_reminders(self):
    """
    Send appointment reminders for today's appointments.
    Scheduled to run daily at 8 AM.

    Returns:
        dict with summary of reminders sent
    """
    try:
        # Import Flask app for context
        from backend.app import create_app
        app = create_app()

        with app.app_context():
            today = date.today()
            logger.info(f"Starting daily reminders for {today}")

            # Get all booked appointments for today
            appointments = Appointment.query.filter(
                Appointment.appointment_date == today,
                Appointment.status == 'booked'
            ).all()

            sent_count = 0
            failed_count = 0
            results = []

            for appointment in appointments:
                try:
                    result = send_appointment_reminder.delay(appointment.id)
                    results.append({
                        'appointment_id': appointment.id,
                        'task_id': result.id,
                        'status': 'queued'
                    })
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to queue reminder for appointment {appointment.id}: {e}")
                    failed_count += 1

            summary = {
                'date': today.isoformat(),
                'total_appointments': len(appointments),
                'reminders_queued': sent_count,
                'failed_to_queue': failed_count,
                'results': results
            }

            logger.info(f"Daily reminders summary: {summary}")
            return summary

    except Exception as e:
        logger.error(f"Error in send_daily_reminders: {e}")
        # Retry on failure
        raise self.retry(exc=e)


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def send_appointment_reminder(self, appointment_id):
    """
    Send reminder for a specific appointment.

    Args:
        appointment_id: ID of the appointment

    Returns:
        dict with success status
    """
    try:
        # Import Flask app for context
        from backend.app import create_app
        app = create_app()

        with app.app_context():
            appointment = Appointment.query.get(appointment_id)

            if not appointment:
                logger.error(f"Appointment {appointment_id} not found")
                return {'success': False, 'message': 'Appointment not found'}

            if appointment.status != 'booked':
                logger.info(f"Appointment {appointment_id} is not booked (status: {appointment.status})")
                return {'success': False, 'message': f'Appointment status is {appointment.status}'}

            patient = appointment.patient
            doctor = appointment.doctor

            if not patient or not patient.user:
                logger.error(f"Patient not found for appointment {appointment_id}")
                return {'success': False, 'message': 'Patient not found'}

            # Send reminder
            result = notification_service.send_appointment_reminder(
                patient_email=patient.user.email,
                patient_name=patient.full_name,
                doctor_name=doctor.full_name if doctor else 'Your Doctor',
                appointment_date=appointment.appointment_date.strftime('%B %d, %Y'),
                appointment_time=appointment.appointment_time.strftime('%I:%M %p'),
                hospital_info={'name': 'Hospital Management System'}
            )

            # Log the notification
            notification_service.log_notification(
                notification_type='appointment_reminder',
                recipient=patient.user.email,
                status=result.get('success', False),
                details={'appointment_id': appointment_id}
            )

            logger.info(f"Reminder sent for appointment {appointment_id}: {result}")
            return result

    except Exception as e:
        logger.error(f"Error sending reminder for appointment {appointment_id}: {e}")
        raise self.retry(exc=e)


@celery.task(bind=True)
def send_booking_confirmation(self, appointment_id):
    """
    Send booking confirmation for a new appointment.

    Args:
        appointment_id: ID of the appointment

    Returns:
        dict with success status
    """
    try:
        from backend.app import create_app
        app = create_app()

        with app.app_context():
            appointment = Appointment.query.get(appointment_id)

            if not appointment:
                return {'success': False, 'message': 'Appointment not found'}

            patient = appointment.patient
            doctor = appointment.doctor

            if not patient or not patient.user:
                return {'success': False, 'message': 'Patient not found'}

            result = notification_service.send_appointment_confirmation(
                patient_email=patient.user.email,
                patient_name=patient.full_name,
                doctor_name=doctor.full_name if doctor else 'Your Doctor',
                appointment_date=appointment.appointment_date.strftime('%B %d, %Y'),
                appointment_time=appointment.appointment_time.strftime('%I:%M %p'),
                appointment_id=appointment.id
            )

            notification_service.log_notification(
                notification_type='appointment_confirmation',
                recipient=patient.user.email,
                status=result.get('success', False),
                details={'appointment_id': appointment_id}
            )

            return result

    except Exception as e:
        logger.error(f"Error sending confirmation for appointment {appointment_id}: {e}")
        return {'success': False, 'message': str(e)}


@celery.task(bind=True)
def send_cancellation_notification(self, appointment_id, reason=None):
    """
    Send cancellation notification for an appointment.

    Args:
        appointment_id: ID of the appointment
        reason: Cancellation reason

    Returns:
        dict with success status
    """
    try:
        from backend.app import create_app
        app = create_app()

        with app.app_context():
            appointment = Appointment.query.get(appointment_id)

            if not appointment:
                return {'success': False, 'message': 'Appointment not found'}

            patient = appointment.patient
            doctor = appointment.doctor

            if not patient or not patient.user:
                return {'success': False, 'message': 'Patient not found'}

            result = notification_service.send_appointment_cancellation(
                patient_email=patient.user.email,
                patient_name=patient.full_name,
                doctor_name=doctor.full_name if doctor else 'Your Doctor',
                appointment_date=appointment.appointment_date.strftime('%B %d, %Y'),
                appointment_time=appointment.appointment_time.strftime('%I:%M %p'),
                reason=reason
            )

            notification_service.log_notification(
                notification_type='appointment_cancellation',
                recipient=patient.user.email,
                status=result.get('success', False),
                details={'appointment_id': appointment_id, 'reason': reason}
            )

            return result

    except Exception as e:
        logger.error(f"Error sending cancellation for appointment {appointment_id}: {e}")
        return {'success': False, 'message': str(e)}
