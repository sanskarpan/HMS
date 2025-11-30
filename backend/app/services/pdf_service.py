"""
PDF generation service for reports and exports.
Uses HTML templates that can be printed to PDF from browser or converted server-side.
"""
import os
from datetime import datetime, date, timedelta
from io import BytesIO


class PDFService:
    """Service for generating PDF-ready HTML reports."""

    @staticmethod
    def get_css_styles():
        """Return common CSS styles for PDF reports."""
        return """
            body {
                font-family: Arial, sans-serif;
                font-size: 12px;
                line-height: 1.5;
                color: #333;
                margin: 0;
                padding: 20px;
            }
            .report-header {
                text-align: center;
                border-bottom: 2px solid #0d6efd;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }
            .report-header h1 {
                color: #0d6efd;
                margin: 0 0 5px 0;
                font-size: 24px;
            }
            .report-header .subtitle {
                color: #666;
                font-size: 14px;
            }
            .report-meta {
                background: #f8f9fa;
                padding: 10px 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .report-meta p {
                margin: 5px 0;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }
            th, td {
                border: 1px solid #dee2e6;
                padding: 8px 12px;
                text-align: left;
            }
            th {
                background: #0d6efd;
                color: white;
                font-weight: bold;
            }
            tr:nth-child(even) {
                background: #f8f9fa;
            }
            .section {
                margin-bottom: 25px;
            }
            .section h2 {
                color: #0d6efd;
                border-bottom: 1px solid #dee2e6;
                padding-bottom: 5px;
                font-size: 16px;
            }
            .stat-box {
                display: inline-block;
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin: 5px;
                min-width: 120px;
                text-align: center;
            }
            .stat-box .value {
                font-size: 24px;
                font-weight: bold;
                color: #0d6efd;
            }
            .stat-box .label {
                font-size: 11px;
                color: #666;
            }
            .footer {
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #dee2e6;
                text-align: center;
                color: #666;
                font-size: 10px;
            }
            @media print {
                body { margin: 0; padding: 15px; }
                .no-print { display: none; }
            }
        """

    @staticmethod
    def generate_monthly_report(stats, month_name, year):
        """
        Generate HTML for monthly hospital report.

        Args:
            stats: Dictionary with appointment/patient/revenue statistics
            month_name: Name of the month
            year: Year number

        Returns:
            HTML string ready for PDF rendering
        """
        css = PDFService.get_css_styles()
        generated_at = datetime.now().strftime('%Y-%m-%d %H:%M')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Monthly Report - {month_name} {year}</title>
            <style>{css}</style>
        </head>
        <body>
            <div class="report-header">
                <h1>Hospital Management System</h1>
                <div class="subtitle">Monthly Report - {month_name} {year}</div>
            </div>

            <div class="report-meta">
                <p><strong>Report Period:</strong> {month_name} {year}</p>
                <p><strong>Generated:</strong> {generated_at}</p>
            </div>

            <div class="section">
                <h2>Summary Statistics</h2>
                <div class="stat-box">
                    <div class="value">{stats.get('total_appointments', 0)}</div>
                    <div class="label">Total Appointments</div>
                </div>
                <div class="stat-box">
                    <div class="value">{stats.get('completed_appointments', 0)}</div>
                    <div class="label">Completed</div>
                </div>
                <div class="stat-box">
                    <div class="value">{stats.get('cancelled_appointments', 0)}</div>
                    <div class="label">Cancelled</div>
                </div>
                <div class="stat-box">
                    <div class="value">{stats.get('new_patients', 0)}</div>
                    <div class="label">New Patients</div>
                </div>
                <div class="stat-box">
                    <div class="value">${stats.get('total_revenue', 0):.2f}</div>
                    <div class="label">Revenue</div>
                </div>
            </div>

            <div class="section">
                <h2>Appointments by Department</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Department</th>
                            <th>Appointments</th>
                            <th>Completed</th>
                            <th>Revenue</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for dept in stats.get('departments', []):
            html += f"""
                        <tr>
                            <td>{dept.get('name', 'N/A')}</td>
                            <td>{dept.get('appointments', 0)}</td>
                            <td>{dept.get('completed', 0)}</td>
                            <td>${dept.get('revenue', 0):.2f}</td>
                        </tr>
            """

        html += """
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>Top Doctors by Appointments</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Doctor</th>
                            <th>Department</th>
                            <th>Appointments</th>
                            <th>Completion Rate</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for doc in stats.get('top_doctors', []):
            completion_rate = (doc.get('completed', 0) / max(doc.get('total', 1), 1)) * 100
            html += f"""
                        <tr>
                            <td>{doc.get('name', 'N/A')}</td>
                            <td>{doc.get('department', 'N/A')}</td>
                            <td>{doc.get('total', 0)}</td>
                            <td>{completion_rate:.1f}%</td>
                        </tr>
            """

        html += f"""
                    </tbody>
                </table>
            </div>

            <div class="footer">
                <p>Hospital Management System - Confidential Report</p>
                <p>Generated on {generated_at}</p>
            </div>

            <div class="no-print" style="text-align: center; margin-top: 20px;">
                <button onclick="window.print()">Print / Save as PDF</button>
            </div>
        </body>
        </html>
        """

        return html

    @staticmethod
    def generate_patient_history(patient, appointments, treatments):
        """
        Generate HTML for patient history report.

        Args:
            patient: Patient object or dict
            appointments: List of appointments
            treatments: List of treatments

        Returns:
            HTML string ready for PDF rendering
        """
        css = PDFService.get_css_styles()
        generated_at = datetime.now().strftime('%Y-%m-%d %H:%M')

        if hasattr(patient, 'to_dict'):
            patient_data = patient.to_dict()
        else:
            patient_data = patient

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Patient History - {patient_data.get('full_name', 'N/A')}</title>
            <style>{css}</style>
        </head>
        <body>
            <div class="report-header">
                <h1>Patient Medical History</h1>
                <div class="subtitle">Medical Record</div>
            </div>

            <div class="report-meta">
                <p><strong>Patient Name:</strong> {patient_data.get('full_name', 'N/A')}</p>
                <p><strong>Date of Birth:</strong> {patient_data.get('date_of_birth', 'N/A')}</p>
                <p><strong>Gender:</strong> {patient_data.get('gender', 'N/A')}</p>
                <p><strong>Blood Group:</strong> {patient_data.get('blood_group', 'N/A')}</p>
                <p><strong>Phone:</strong> {patient_data.get('phone', 'N/A')}</p>
                <p><strong>Generated:</strong> {generated_at}</p>
            </div>

            <div class="section">
                <h2>Medical History Notes</h2>
                <p>{patient_data.get('medical_history', 'No medical history recorded.')}</p>
            </div>

            <div class="section">
                <h2>Appointment History</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Doctor</th>
                            <th>Department</th>
                            <th>Status</th>
                            <th>Reason</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for apt in appointments:
            apt_data = apt if isinstance(apt, dict) else apt.to_dict(include_doctor=True)
            doctor_name = 'N/A'
            dept_name = 'N/A'

            if isinstance(apt_data.get('doctor'), dict):
                doctor_name = apt_data['doctor'].get('full_name', 'N/A')
                if isinstance(apt_data['doctor'].get('department'), dict):
                    dept_name = apt_data['doctor']['department'].get('name', 'N/A')

            html += f"""
                        <tr>
                            <td>{apt_data.get('appointment_date', 'N/A')}</td>
                            <td>{apt_data.get('appointment_time', 'N/A')}</td>
                            <td>{doctor_name}</td>
                            <td>{dept_name}</td>
                            <td>{apt_data.get('status', 'N/A').title()}</td>
                            <td>{apt_data.get('reason', 'N/A')[:50]}...</td>
                        </tr>
            """

        html += """
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>Treatment Records</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Doctor</th>
                            <th>Diagnosis</th>
                            <th>Prescription</th>
                            <th>Follow-up</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for t in treatments:
            t_data = t if isinstance(t, dict) else t.to_dict(include_appointment=True)
            apt_date = 'N/A'
            doctor_name = 'N/A'

            if isinstance(t_data.get('appointment'), dict):
                apt_date = t_data['appointment'].get('appointment_date', 'N/A')
                if isinstance(t_data['appointment'].get('doctor'), dict):
                    doctor_name = t_data['appointment']['doctor'].get('full_name', 'N/A')

            diagnosis = t_data.get('diagnosis', 'N/A')
            if len(diagnosis) > 50:
                diagnosis = diagnosis[:50] + '...'

            prescription = t_data.get('prescription', 'N/A') or 'N/A'
            if len(prescription) > 50:
                prescription = prescription[:50] + '...'

            html += f"""
                        <tr>
                            <td>{apt_date}</td>
                            <td>{doctor_name}</td>
                            <td>{diagnosis}</td>
                            <td>{prescription}</td>
                            <td>{t_data.get('follow_up_date', 'None')}</td>
                        </tr>
            """

        html += f"""
                    </tbody>
                </table>
            </div>

            <div class="footer">
                <p>Hospital Management System - Confidential Patient Record</p>
                <p>Generated on {generated_at}</p>
            </div>

            <div class="no-print" style="text-align: center; margin-top: 20px;">
                <button onclick="window.print()">Print / Save as PDF</button>
            </div>
        </body>
        </html>
        """

        return html

    @staticmethod
    def generate_doctor_report(doctor, stats, appointments):
        """
        Generate HTML for doctor activity report.

        Args:
            doctor: Doctor object or dict
            stats: Statistics dict
            appointments: List of recent appointments

        Returns:
            HTML string ready for PDF rendering
        """
        css = PDFService.get_css_styles()
        generated_at = datetime.now().strftime('%Y-%m-%d %H:%M')

        if hasattr(doctor, 'to_dict'):
            doctor_data = doctor.to_dict(include_department=True)
        else:
            doctor_data = doctor

        dept_name = 'N/A'
        if isinstance(doctor_data.get('department'), dict):
            dept_name = doctor_data['department'].get('name', 'N/A')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Doctor Report - {doctor_data.get('full_name', 'N/A')}</title>
            <style>{css}</style>
        </head>
        <body>
            <div class="report-header">
                <h1>Doctor Activity Report</h1>
                <div class="subtitle">{doctor_data.get('full_name', 'N/A')}</div>
            </div>

            <div class="report-meta">
                <p><strong>Doctor:</strong> {doctor_data.get('full_name', 'N/A')}</p>
                <p><strong>Department:</strong> {dept_name}</p>
                <p><strong>Qualification:</strong> {doctor_data.get('qualification', 'N/A')}</p>
                <p><strong>Experience:</strong> {doctor_data.get('experience_years', 0)} years</p>
                <p><strong>Generated:</strong> {generated_at}</p>
            </div>

            <div class="section">
                <h2>Performance Summary</h2>
                <div class="stat-box">
                    <div class="value">{stats.get('total_appointments', 0)}</div>
                    <div class="label">Total Appointments</div>
                </div>
                <div class="stat-box">
                    <div class="value">{stats.get('completed', 0)}</div>
                    <div class="label">Completed</div>
                </div>
                <div class="stat-box">
                    <div class="value">{stats.get('cancelled', 0)}</div>
                    <div class="label">Cancelled</div>
                </div>
                <div class="stat-box">
                    <div class="value">{stats.get('unique_patients', 0)}</div>
                    <div class="label">Unique Patients</div>
                </div>
            </div>

            <div class="section">
                <h2>Recent Appointments</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Patient</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for apt in appointments[:20]:
            apt_data = apt if isinstance(apt, dict) else apt.to_dict(include_patient=True)
            patient_name = 'N/A'
            if isinstance(apt_data.get('patient'), dict):
                patient_name = apt_data['patient'].get('full_name', 'N/A')

            html += f"""
                        <tr>
                            <td>{apt_data.get('appointment_date', 'N/A')}</td>
                            <td>{apt_data.get('appointment_time', 'N/A')}</td>
                            <td>{patient_name}</td>
                            <td>{apt_data.get('status', 'N/A').title()}</td>
                        </tr>
            """

        html += f"""
                    </tbody>
                </table>
            </div>

            <div class="footer">
                <p>Hospital Management System - Doctor Activity Report</p>
                <p>Generated on {generated_at}</p>
            </div>

            <div class="no-print" style="text-align: center; margin-top: 20px;">
                <button onclick="window.print()">Print / Save as PDF</button>
            </div>
        </body>
        </html>
        """

        return html

    @staticmethod
    def generate_appointment_receipt(appointment, payment=None):
        """
        Generate HTML receipt for appointment payment.

        Args:
            appointment: Appointment object or dict
            payment: Payment object or dict (optional)

        Returns:
            HTML string ready for PDF rendering
        """
        css = PDFService.get_css_styles()
        generated_at = datetime.now().strftime('%Y-%m-%d %H:%M')

        if hasattr(appointment, 'to_dict'):
            apt_data = appointment.to_dict(include_patient=True, include_doctor=True)
        else:
            apt_data = appointment

        patient_name = 'N/A'
        doctor_name = 'N/A'
        dept_name = 'N/A'

        if isinstance(apt_data.get('patient'), dict):
            patient_name = apt_data['patient'].get('full_name', 'N/A')

        if isinstance(apt_data.get('doctor'), dict):
            doctor_name = apt_data['doctor'].get('full_name', 'N/A')
            if isinstance(apt_data['doctor'].get('department'), dict):
                dept_name = apt_data['doctor']['department'].get('name', 'N/A')

        payment_data = {}
        if payment:
            if hasattr(payment, 'to_dict'):
                payment_data = payment.to_dict()
            else:
                payment_data = payment

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Appointment Receipt</title>
            <style>{css}</style>
        </head>
        <body>
            <div class="report-header">
                <h1>Appointment Receipt</h1>
                <div class="subtitle">Hospital Management System</div>
            </div>

            <div class="report-meta">
                <p><strong>Receipt Date:</strong> {generated_at}</p>
                <p><strong>Appointment ID:</strong> {apt_data.get('id', 'N/A')}</p>
                <p><strong>Transaction ID:</strong> {payment_data.get('transaction_id', 'N/A')}</p>
            </div>

            <div class="section">
                <h2>Appointment Details</h2>
                <table>
                    <tr>
                        <td><strong>Patient Name:</strong></td>
                        <td>{patient_name}</td>
                    </tr>
                    <tr>
                        <td><strong>Doctor:</strong></td>
                        <td>{doctor_name}</td>
                    </tr>
                    <tr>
                        <td><strong>Department:</strong></td>
                        <td>{dept_name}</td>
                    </tr>
                    <tr>
                        <td><strong>Date:</strong></td>
                        <td>{apt_data.get('appointment_date', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Time:</strong></td>
                        <td>{apt_data.get('appointment_time', 'N/A')}</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>Payment Information</h2>
                <table>
                    <tr>
                        <td><strong>Amount:</strong></td>
                        <td>${payment_data.get('amount', 0):.2f}</td>
                    </tr>
                    <tr>
                        <td><strong>Payment Method:</strong></td>
                        <td>{payment_data.get('payment_method', 'N/A').title()}</td>
                    </tr>
                    <tr>
                        <td><strong>Status:</strong></td>
                        <td>{payment_data.get('status', 'N/A').title()}</td>
                    </tr>
                    <tr>
                        <td><strong>Paid At:</strong></td>
                        <td>{payment_data.get('paid_at', 'N/A')}</td>
                    </tr>
                </table>
            </div>

            <div class="footer">
                <p>Thank you for choosing our hospital.</p>
                <p>This is a computer-generated receipt.</p>
            </div>

            <div class="no-print" style="text-align: center; margin-top: 20px;">
                <button onclick="window.print()">Print Receipt</button>
            </div>
        </body>
        </html>
        """

        return html
