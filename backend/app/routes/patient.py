"""
Patient API routes for the Hospital Management System.
Handles patient dashboard, profile, doctor search, appointment booking, and treatment history.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta, time

from backend.app.models import (
    db, User, Patient, Doctor, Department,
    Appointment, Treatment, DoctorAvailability
)
from backend.app.utils import (
    patient_required,
    get_current_user_from_request
)

patient_bp = Blueprint('patient', __name__)


def get_current_patient():
    """Get the patient profile for the current authenticated user."""
    user = get_current_user_from_request()
    if user and user.patient_profile:
        return user.patient_profile
    return None


# =============================================================================
# Dashboard & Profile
# =============================================================================

@patient_bp.route('/dashboard/stats', methods=['GET'])
@patient_required
def get_dashboard_stats():
    """Get patient dashboard statistics."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    today = date.today()

    # Upcoming appointments
    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date >= today,
        Appointment.status == 'booked'
    ).count()

    # Completed appointments
    completed = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == 'completed'
    ).count()

    # Today's appointments
    today_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date == today,
        Appointment.status == 'booked'
    ).order_by(Appointment.appointment_time).all()

    # Total treatments
    total_treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient.id
    ).count()

    return jsonify({
        'success': True,
        'stats': {
            'upcoming_appointments': upcoming,
            'completed_appointments': completed,
            'total_treatments': total_treatments,
            'today_appointments': [apt.to_dict(include_doctor=True) for apt in today_appointments]
        }
    }), 200


@patient_bp.route('/profile', methods=['GET'])
@patient_required
def get_profile():
    """Get current patient's profile."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    return jsonify({
        'success': True,
        'patient': patient.to_dict(include_user=True)
    }), 200


@patient_bp.route('/profile', methods=['PUT'])
@patient_required
def update_profile():
    """Update patient's profile."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    data = request.get_json()

    # Updatable fields
    updatable_fields = ['full_name', 'phone', 'address', 'emergency_contact',
                        'blood_group', 'medical_history', 'gender']

    for field in updatable_fields:
        if field in data:
            setattr(patient, field, data[field])

    # Handle date_of_birth separately
    if 'date_of_birth' in data:
        try:
            if data['date_of_birth']:
                patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            else:
                patient.date_of_birth = None
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'patient': patient.to_dict(include_user=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
