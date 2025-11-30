"""
Reports routes - PDF report generation and export endpoints
"""
from flask import Blueprint, request, jsonify, Response
from datetime import datetime, date, timedelta

from backend.app.models import (
    db, Doctor, Patient, Appointment, Treatment, Department, Payment
)
from backend.app.utils.decorators import admin_required, doctor_required, patient_required
from backend.app.utils import get_current_user_from_request
from backend.app.services.pdf_service import PDFService

reports_bp = Blueprint('reports', __name__)


def get_current_patient():
    """Return patient profile for logged-in user."""
    user = get_current_user_from_request()
    if user and user.patient_profile:
        return user.patient_profile
    return None


def get_current_doctor():
    """Return doctor profile for logged-in user."""
    user = get_current_user_from_request()
    if user and user.doctor_profile:
        return user.doctor_profile
    return None


@reports_bp.route('/admin/monthly', methods=['GET'])
@admin_required
def get_monthly_report():
    """Generate monthly hospital report HTML for PDF."""
    from sqlalchemy import func, extract

    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    if not month or not year:
        today = date.today()
        month = today.month
        year = today.year

    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    month_name = month_names[month - 1]

    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    total_apts = Appointment.query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    ).count()

    completed_apts = Appointment.query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date,
        Appointment.status == 'completed'
    ).count()

    cancelled_apts = Appointment.query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date,
        Appointment.status == 'cancelled'
    ).count()

    new_patients = Patient.query.filter(
        func.date(Patient.created_at) >= start_date,
        func.date(Patient.created_at) <= end_date
    ).count()

    revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'completed',
        func.date(Payment.paid_at) >= start_date,
        func.date(Payment.paid_at) <= end_date
    ).scalar() or 0

    dept_stats = []
    departments = Department.get_all_active()
    for dept in departments:
        dept_apts = Appointment.query.filter(
            Appointment.department_id == dept.id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).count()

        dept_completed = Appointment.query.filter(
            Appointment.department_id == dept.id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date,
            Appointment.status == 'completed'
        ).count()

        dept_revenue = db.session.query(func.sum(Payment.amount)).join(
            Appointment, Payment.appointment_id == Appointment.id
        ).filter(
            Appointment.department_id == dept.id,
            Payment.status == 'completed',
            func.date(Payment.paid_at) >= start_date,
            func.date(Payment.paid_at) <= end_date
        ).scalar() or 0

        dept_stats.append({
            'name': dept.name,
            'appointments': dept_apts,
            'completed': dept_completed,
            'revenue': dept_revenue
        })

    top_doctors = db.session.query(
        Doctor.full_name,
        Department.name,
        func.count(Appointment.id).label('total'),
        func.sum(db.case(
            (Appointment.status == 'completed', 1),
            else_=0
        )).label('completed')
    ).join(
        Appointment, Doctor.id == Appointment.doctor_id
    ).join(
        Department, Doctor.department_id == Department.id
    ).filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    ).group_by(
        Doctor.id, Doctor.full_name, Department.name
    ).order_by(
        func.count(Appointment.id).desc()
    ).limit(10).all()

    top_doctors_list = [
        {
            'name': doc[0],
            'department': doc[1],
            'total': doc[2],
            'completed': doc[3] or 0
        }
        for doc in top_doctors
    ]

    stats = {
        'total_appointments': total_apts,
        'completed_appointments': completed_apts,
        'cancelled_appointments': cancelled_apts,
        'new_patients': new_patients,
        'total_revenue': revenue,
        'departments': dept_stats,
        'top_doctors': top_doctors_list
    }

    html = PDFService.generate_monthly_report(stats, month_name, year)

    return Response(html, mimetype='text/html')


@reports_bp.route('/admin/monthly/data', methods=['GET'])
@admin_required
def get_monthly_report_data():
    """Get monthly report data as JSON."""
    from sqlalchemy import func

    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    if not month or not year:
        today = date.today()
        month = today.month
        year = today.year

    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    total_apts = Appointment.query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    ).count()

    completed_apts = Appointment.query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date,
        Appointment.status == 'completed'
    ).count()

    cancelled_apts = Appointment.query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date,
        Appointment.status == 'cancelled'
    ).count()

    revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'completed',
        func.date(Payment.paid_at) >= start_date,
        func.date(Payment.paid_at) <= end_date
    ).scalar() or 0

    return jsonify({
        'success': True,
        'report': {
            'month': month,
            'year': year,
            'total_appointments': total_apts,
            'completed_appointments': completed_apts,
            'cancelled_appointments': cancelled_apts,
            'total_revenue': revenue
        }
    }), 200


@reports_bp.route('/patient/history', methods=['GET'])
@patient_required
def get_patient_history_report():
    """Generate patient history HTML for PDF."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    appointments = Appointment.query.filter_by(
        patient_id=patient.id
    ).order_by(
        Appointment.appointment_date.desc()
    ).all()

    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient.id
    ).order_by(
        Appointment.appointment_date.desc()
    ).all()

    apt_list = [apt.to_dict(include_doctor=True) for apt in appointments]
    treatment_list = [t.to_dict(include_appointment=True) for t in treatments]

    html = PDFService.generate_patient_history(patient, apt_list, treatment_list)

    return Response(html, mimetype='text/html')


@reports_bp.route('/patient/receipt/<int:payment_id>', methods=['GET'])
@patient_required
def get_payment_receipt(payment_id):
    """Generate payment receipt HTML for PDF."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    payment = Payment.query.filter_by(
        id=payment_id,
        patient_id=patient.id
    ).first()

    if not payment:
        return jsonify({'success': False, 'message': 'Payment not found'}), 404

    appointment = payment.appointment

    html = PDFService.generate_appointment_receipt(appointment, payment)

    return Response(html, mimetype='text/html')


@reports_bp.route('/doctor/activity', methods=['GET'])
@doctor_required
def get_doctor_activity_report():
    """Generate doctor activity report HTML for PDF."""
    from sqlalchemy import func

    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    days = request.args.get('days', 30, type=int)
    start_date = date.today() - timedelta(days=days)

    total_apts = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= start_date
    ).count()

    completed = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= start_date,
        Appointment.status == 'completed'
    ).count()

    cancelled = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= start_date,
        Appointment.status == 'cancelled'
    ).count()

    unique_patients = db.session.query(Appointment.patient_id).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= start_date
    ).distinct().count()

    stats = {
        'total_appointments': total_apts,
        'completed': completed,
        'cancelled': cancelled,
        'unique_patients': unique_patients
    }

    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= start_date
    ).order_by(
        Appointment.appointment_date.desc()
    ).limit(50).all()

    apt_list = [apt.to_dict(include_patient=True) for apt in appointments]

    html = PDFService.generate_doctor_report(doctor, stats, apt_list)

    return Response(html, mimetype='text/html')


@reports_bp.route('/admin/patient/<int:patient_id>/history', methods=['GET'])
@admin_required
def admin_get_patient_history(patient_id):
    """Admin: Generate patient history HTML for PDF."""
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'success': False, 'message': 'Patient not found'}), 404

    appointments = Appointment.query.filter_by(
        patient_id=patient.id
    ).order_by(
        Appointment.appointment_date.desc()
    ).all()

    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient.id
    ).order_by(
        Appointment.appointment_date.desc()
    ).all()

    apt_list = [apt.to_dict(include_doctor=True) for apt in appointments]
    treatment_list = [t.to_dict(include_appointment=True) for t in treatments]

    html = PDFService.generate_patient_history(patient, apt_list, treatment_list)

    return Response(html, mimetype='text/html')
