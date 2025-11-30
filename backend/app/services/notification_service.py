"""
Notification Service for Hospital Management System.
Provides methods for sending emails, webhooks, and other notifications.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import json
import urllib.request
import urllib.error

from backend.config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class NotificationService:
    """Service for sending notifications via various channels."""

    # Template directory
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates', 'emails')

    def __init__(self):
        """Initialize the notification service."""
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.TEMPLATE_DIR),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def send_email(self, to, subject, body, html=None, attachments=None):
        """
        Send an email using configured SMTP server.

        Args:
            to: Recipient email address (string or list)
            subject: Email subject
            body: Plain text body
            html: Optional HTML body
            attachments: Optional list of (filename, content, mimetype) tuples

        Returns:
            dict with success status and message
        """
        try:
            # Validate configuration
            if not config.MAIL_USERNAME or not config.MAIL_PASSWORD:
                logger.warning("Email credentials not configured, simulating send")
                return self._simulate_email_send(to, subject, body)

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = config.MAIL_DEFAULT_SENDER or config.MAIL_USERNAME
            msg['To'] = to if isinstance(to, str) else ', '.join(to)

            # Attach plain text body
            msg.attach(MIMEText(body, 'plain'))

            # Attach HTML if provided
            if html:
                msg.attach(MIMEText(html, 'html'))

            # Attach files if provided
            if attachments:
                for filename, content, mimetype in attachments:
                    part = MIMEBase(*mimetype.split('/'))
                    part.set_payload(content)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(part)

            # Send email
            with smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT) as server:
                if config.MAIL_USE_TLS:
                    server.starttls()
                server.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
                recipients = [to] if isinstance(to, str) else to
                server.sendmail(config.MAIL_USERNAME, recipients, msg.as_string())

            logger.info(f"Email sent successfully to {to}")
            return {'success': True, 'message': 'Email sent successfully'}

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            # In development mode, simulate send instead of failing
            logger.warning("Falling back to simulated email send")
            return self._simulate_email_send(to, subject, body)
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return {'success': False, 'message': f'Failed to send email: {str(e)}'}
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return {'success': False, 'message': f'Error: {str(e)}'}

    def _simulate_email_send(self, to, subject, body):
        """Simulate email sending when credentials are not configured."""
        logger.info(f"[SIMULATED] Email to: {to}")
        logger.info(f"[SIMULATED] Subject: {subject}")
        logger.info(f"[SIMULATED] Body preview: {body[:100]}...")
        return {'success': True, 'message': 'Email simulated (no credentials configured)', 'simulated': True}

    def send_gchat_webhook(self, webhook_url, message):
        """
        Send a message to Google Chat via webhook.

        Args:
            webhook_url: Google Chat webhook URL
            message: Message text to send

        Returns:
            dict with success status and message
        """
        try:
            if not webhook_url:
                logger.warning("Google Chat webhook URL not configured")
                return {'success': False, 'message': 'Webhook URL not configured'}

            data = json.dumps({'text': message}).encode('utf-8')
            req = urllib.request.Request(
                webhook_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    logger.info("Google Chat message sent successfully")
                    return {'success': True, 'message': 'Webhook message sent'}
                else:
                    return {'success': False, 'message': f'Webhook returned status {response.status}'}

        except urllib.error.URLError as e:
            logger.error(f"Webhook URL error: {e}")
            return {'success': False, 'message': f'Webhook error: {str(e)}'}
        except Exception as e:
            logger.error(f"Unexpected webhook error: {e}")
            return {'success': False, 'message': f'Error: {str(e)}'}

    def send_appointment_reminder(self, patient_email, patient_name, doctor_name,
                                   appointment_date, appointment_time, hospital_info=None):
        """
        Send appointment reminder email to patient.

        Args:
            patient_email: Patient's email address
            patient_name: Patient's name
            doctor_name: Doctor's name
            appointment_date: Date of appointment
            appointment_time: Time of appointment
            hospital_info: Optional hospital information dict

        Returns:
            dict with success status
        """
        subject = f"Appointment Reminder - {appointment_date}"

        # Plain text body
        body = f"""Dear {patient_name},

This is a reminder for your upcoming appointment:

Doctor: {doctor_name}
Date: {appointment_date}
Time: {appointment_time}

Please arrive 15 minutes before your scheduled time.

Hospital Management System
"""

        # Try to load HTML template
        html = None
        try:
            template = self.jinja_env.get_template('appointment_reminder.html')
            html = template.render(
                patient_name=patient_name,
                doctor_name=doctor_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                hospital_info=hospital_info or {}
            )
        except Exception as e:
            logger.warning(f"Could not load email template: {e}")

        return self.send_email(patient_email, subject, body, html)

    def send_appointment_confirmation(self, patient_email, patient_name, doctor_name,
                                       appointment_date, appointment_time, appointment_id):
        """
        Send appointment confirmation email to patient.

        Args:
            patient_email: Patient's email address
            patient_name: Patient's name
            doctor_name: Doctor's name
            appointment_date: Date of appointment
            appointment_time: Time of appointment
            appointment_id: Appointment reference ID

        Returns:
            dict with success status
        """
        subject = f"Appointment Confirmed - Reference #{appointment_id}"

        body = f"""Dear {patient_name},

Your appointment has been confirmed:

Reference ID: #{appointment_id}
Doctor: {doctor_name}
Date: {appointment_date}
Time: {appointment_time}

Please save this reference for your records.

Hospital Management System
"""

        html = None
        try:
            template = self.jinja_env.get_template('appointment_confirmation.html')
            html = template.render(
                patient_name=patient_name,
                doctor_name=doctor_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                appointment_id=appointment_id
            )
        except Exception as e:
            logger.warning(f"Could not load email template: {e}")

        return self.send_email(patient_email, subject, body, html)

    def send_appointment_cancellation(self, patient_email, patient_name, doctor_name,
                                       appointment_date, appointment_time, reason=None):
        """
        Send appointment cancellation notification.

        Args:
            patient_email: Patient's email address
            patient_name: Patient's name
            doctor_name: Doctor's name
            appointment_date: Original appointment date
            appointment_time: Original appointment time
            reason: Optional cancellation reason

        Returns:
            dict with success status
        """
        subject = f"Appointment Cancelled - {appointment_date}"

        body = f"""Dear {patient_name},

Your appointment has been cancelled:

Doctor: {doctor_name}
Date: {appointment_date}
Time: {appointment_time}
"""
        if reason:
            body += f"\nReason: {reason}"

        body += """

Please book a new appointment if needed.

Hospital Management System
"""

        html = None
        try:
            template = self.jinja_env.get_template('appointment_cancellation.html')
            html = template.render(
                patient_name=patient_name,
                doctor_name=doctor_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason
            )
        except Exception as e:
            logger.warning(f"Could not load email template: {e}")

        return self.send_email(patient_email, subject, body, html)

    def send_monthly_report(self, doctor_email, doctor_name, month, year,
                            report_html, report_pdf=None):
        """
        Send monthly activity report to doctor.

        Args:
            doctor_email: Doctor's email address
            doctor_name: Doctor's name
            month: Report month (1-12)
            year: Report year
            report_html: HTML content of the report
            report_pdf: Optional PDF content as bytes

        Returns:
            dict with success status
        """
        month_name = datetime(year, month, 1).strftime('%B')
        subject = f"Monthly Activity Report - {month_name} {year}"

        body = f"""Dear Dr. {doctor_name},

Please find attached your monthly activity report for {month_name} {year}.

This report includes:
- Total appointments
- Completed vs cancelled appointments
- Patient list with diagnoses
- Treatment summary

Hospital Management System
"""

        attachments = []
        if report_pdf:
            attachments.append((
                f'monthly_report_{year}_{month:02d}.pdf',
                report_pdf,
                'application/pdf'
            ))

        return self.send_email(doctor_email, subject, body, report_html, attachments)

    def send_export_ready(self, patient_email, patient_name, download_url, expiry_hours=24):
        """
        Notify patient that their data export is ready.

        Args:
            patient_email: Patient's email address
            patient_name: Patient's name
            download_url: URL to download the export
            expiry_hours: Hours until download link expires

        Returns:
            dict with success status
        """
        subject = "Your Data Export is Ready"

        body = f"""Dear {patient_name},

Your requested data export is ready for download.

Download Link: {download_url}

This link will expire in {expiry_hours} hours.

Hospital Management System
"""

        return self.send_email(patient_email, subject, body)

    def log_notification(self, notification_type, recipient, status, details=None):
        """
        Log a notification for audit purposes.

        Args:
            notification_type: Type of notification (email, webhook, etc.)
            recipient: Recipient identifier
            status: Success/failure status
            details: Optional additional details
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': notification_type,
            'recipient': recipient,
            'status': 'success' if status else 'failure',
            'details': details
        }
        logger.info(f"Notification log: {json.dumps(log_entry)}")


# Singleton instance
notification_service = NotificationService()
