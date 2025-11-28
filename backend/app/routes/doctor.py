"""
Doctor API Routes for the Hospital Management System.
Handles doctor dashboard, appointments, patients, treatments, and availability.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, time, timedelta

from backend.app.models import (
    db, User, Doctor, Patient, Appointment, Treatment, DoctorAvailability
)
from backend.app.utils.decorators import doctor_required, get_current_user_from_request


doctor_bp = Blueprint('doctor', __name__)


# ============================================================================
# Helper function to get current doctor
# ============================================================================

def get_current_doctor():
    """Get the doctor profile for the current authenticated user."""
    user = get_current_user_from_request()
    if user and user.doctor_profile:
        return user.doctor_profile
    return None


# ============================================================================
# Dashboard
# ============================================================================

@doctor_bp.route('/dashboard/stats', methods=['GET'])
@doctor_required
def get_dashboard_stats():
    """
    Get doctor dashboard statistics.

    Returns:
        Today's appointments, week's appointments, total patients,
        pending appointments, and recent activity.
    """
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found'
        }), 404

    today = date.today()
    week_end = today + timedelta(days=7)

    # Today's appointments
    today_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date == today
    ).all()

    # This week's appointments
    week_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= today,
        Appointment.appointment_date < week_end,
        Appointment.status == 'booked'
    ).count()

    # Total unique patients
    total_patients = db.session.query(Appointment.patient_id).filter(
        Appointment.doctor_id == doctor.id
    ).distinct().count()

    # Pending (booked) appointments
    pending = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status == 'booked',
        Appointment.appointment_date >= today
    ).count()

    # Completed appointments
    completed = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status == 'completed'
    ).count()

    return jsonify({
        'success': True,
        'stats': {
            'today_appointments': len(today_appointments),
            'today_appointments_list': [
                apt.to_dict(include_patient=True) for apt in today_appointments
            ],
            'week_appointments': week_appointments,
            'total_patients': total_patients,
            'pending_appointments': pending,
            'completed_appointments': completed
        },
        'doctor': {
            'id': doctor.id,
            'full_name': doctor.full_name,
            'department': doctor.department.name if doctor.department else None
        }
    }), 200

