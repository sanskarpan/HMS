"""
Monthly report generation tasks for Hospital Management System.
"""
import logging
from datetime import datetime, date
from calendar import monthrange
from celery import shared_task
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

from backend.celery_app import celery
from backend.app.models import db, Appointment, Patient, Doctor, Treatment
from backend.app.services.notification_service import notification_service

logger = logging.getLogger(__name__)

# Template directory
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates', 'reports')


@celery.task(bind=True, max_retries=3, default_retry_delay=300)
def send_monthly_reports(self):
    """
    Generate and send monthly reports to all doctors.
    Scheduled to run on the 1st of each month at 9 AM.

    Returns:
        dict with summary of reports sent
    """
    try:
        from backend.app import create_app
        app = create_app()

        with app.app_context():
            # Get previous month
            today = date.today()
            if today.month == 1:
                report_month = 12
                report_year = today.year - 1
            else:
                report_month = today.month - 1
                report_year = today.year

            logger.info(f"Generating monthly reports for {report_month}/{report_year}")

            # Get all active doctors
            doctors = Doctor.query.filter(Doctor.is_active == True).all()

            sent_count = 0
            failed_count = 0
            results = []

            for doctor in doctors:
                try:
                    result = generate_monthly_report.delay(
                        doctor.id, report_month, report_year
                    )
                    results.append({
                        'doctor_id': doctor.id,
                        'doctor_name': doctor.full_name,
                        'task_id': result.id,
                        'status': 'queued'
                    })
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to queue report for doctor {doctor.id}: {e}")
                    failed_count += 1

            summary = {
                'month': report_month,
                'year': report_year,
                'total_doctors': len(doctors),
                'reports_queued': sent_count,
                'failed_to_queue': failed_count,
                'results': results
            }

            logger.info(f"Monthly reports summary: {summary}")
            return summary

    except Exception as e:
        logger.error(f"Error in send_monthly_reports: {e}")
        raise self.retry(exc=e)


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_monthly_report(self, doctor_id, month, year):
    """
    Generate and send monthly activity report for a specific doctor.

    Args:
        doctor_id: ID of the doctor
        month: Report month (1-12)
        year: Report year

    Returns:
        dict with success status
    """
    try:
        from backend.app import create_app
        app = create_app()

        with app.app_context():
            doctor = Doctor.query.get(doctor_id)

            if not doctor:
                logger.error(f"Doctor {doctor_id} not found")
                return {'success': False, 'message': 'Doctor not found'}

            if not doctor.user:
                logger.error(f"Doctor {doctor_id} has no user account")
                return {'success': False, 'message': 'Doctor user not found'}

            # Get date range for the month
            _, last_day = monthrange(year, month)
            start_date = date(year, month, 1)
            end_date = date(year, month, last_day)

            # Get all appointments for this doctor in this month
            appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date
            ).order_by(Appointment.appointment_date).all()

            # Calculate statistics
            total_appointments = len(appointments)
            completed = sum(1 for a in appointments if a.status == 'completed')
            cancelled = sum(1 for a in appointments if a.status == 'cancelled')
            no_show = sum(1 for a in appointments if a.status == 'no_show')
            booked = sum(1 for a in appointments if a.status == 'booked')

            # Get unique patients
            patient_ids = set(a.patient_id for a in appointments)
            new_patients = 0

            for patient_id in patient_ids:
                # Check if this was their first appointment with this doctor
                first_apt = Appointment.query.filter(
                    Appointment.patient_id == patient_id,
                    Appointment.doctor_id == doctor_id
                ).order_by(Appointment.appointment_date).first()

                if first_apt and start_date <= first_apt.appointment_date <= end_date:
                    new_patients += 1

            # Build appointment details with treatments
            appointment_details = []
            for apt in appointments:
                if apt.status == 'completed':
                    treatment = Treatment.query.filter_by(appointment_id=apt.id).first()
                    appointment_details.append({
                        'date': apt.appointment_date.strftime('%Y-%m-%d'),
                        'time': apt.appointment_time.strftime('%H:%M'),
                        'patient_name': apt.patient.full_name if apt.patient else 'Unknown',
                        'status': apt.status,
                        'diagnosis': treatment.diagnosis if treatment else 'N/A',
                        'treatment': treatment.prescription if treatment else 'N/A'
                    })

            # Generate report data
            report_data = {
                'doctor_name': doctor.full_name,
                'department': doctor.department.name if doctor.department else 'N/A',
                'qualification': doctor.qualification or 'N/A',
                'month_name': datetime(year, month, 1).strftime('%B'),
                'year': year,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'statistics': {
                    'total_appointments': total_appointments,
                    'completed': completed,
                    'cancelled': cancelled,
                    'no_show': no_show,
                    'pending': booked,
                    'total_patients': len(patient_ids),
                    'new_patients': new_patients,
                    'completion_rate': round(completed / total_appointments * 100, 1) if total_appointments > 0 else 0
                },
                'appointments': appointment_details
            }

            # Render HTML report
            try:
                jinja_env = Environment(
                    loader=FileSystemLoader(TEMPLATE_DIR),
                    autoescape=select_autoescape(['html', 'xml'])
                )
                template = jinja_env.get_template('monthly_report.html')
                report_html = template.render(**report_data)
            except Exception as e:
                logger.warning(f"Could not render HTML template: {e}")
                report_html = _generate_simple_html_report(report_data)

            # Send the report
            result = notification_service.send_monthly_report(
                doctor_email=doctor.user.email,
                doctor_name=doctor.full_name,
                month=month,
                year=year,
                report_html=report_html
            )

            notification_service.log_notification(
                notification_type='monthly_report',
                recipient=doctor.user.email,
                status=result.get('success', False),
                details={'doctor_id': doctor_id, 'month': month, 'year': year}
            )

            logger.info(f"Monthly report sent to doctor {doctor_id}: {result}")
            return {
                'success': result.get('success', False),
                'doctor_id': doctor_id,
                'month': month,
                'year': year,
                'statistics': report_data['statistics']
            }

    except Exception as e:
        logger.error(f"Error generating report for doctor {doctor_id}: {e}")
        raise self.retry(exc=e)


def _generate_simple_html_report(data):
    """Generate a simple HTML report when template is not available."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Monthly Report - {data['month_name']} {data['year']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #0d6efd; }}
            .stats {{ background: #f8f9fa; padding: 20px; margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background: #0d6efd; color: white; }}
        </style>
    </head>
    <body>
        <h1>Monthly Activity Report</h1>
        <h2>Dr. {data['doctor_name']}</h2>
        <p>Department: {data['department']} | Period: {data['month_name']} {data['year']}</p>

        <div class="stats">
            <h3>Summary Statistics</h3>
            <ul>
                <li>Total Appointments: {data['statistics']['total_appointments']}</li>
                <li>Completed: {data['statistics']['completed']}</li>
                <li>Cancelled: {data['statistics']['cancelled']}</li>
                <li>No Show: {data['statistics']['no_show']}</li>
                <li>Total Patients: {data['statistics']['total_patients']}</li>
                <li>New Patients: {data['statistics']['new_patients']}</li>
                <li>Completion Rate: {data['statistics']['completion_rate']}%</li>
            </ul>
        </div>

        <h3>Completed Appointments</h3>
        <table>
            <tr>
                <th>Date</th>
                <th>Patient</th>
                <th>Diagnosis</th>
                <th>Treatment</th>
            </tr>
            {''.join(f"<tr><td>{apt['date']}</td><td>{apt['patient_name']}</td><td>{apt['diagnosis']}</td><td>{apt['treatment']}</td></tr>" for apt in data['appointments'])}
        </table>

        <p><small>Generated on {data['generated_at']}</small></p>
    </body>
    </html>
    """
