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


# =============================================================================
# Doctor Search & Availability
# =============================================================================

@patient_bp.route('/departments', methods=['GET'])
@patient_required
def get_departments():
    """Get all departments/specializations."""
    departments = Department.query.order_by(Department.name).all()

    result = []
    for dept in departments:
        doctor_count = Doctor.query.filter_by(department_id=dept.id, is_active=True).count()
        result.append({
            'id': dept.id,
            'name': dept.name,
            'description': dept.description,
            'doctor_count': doctor_count
        })

    return jsonify({
        'success': True,
        'departments': result
    }), 200


@patient_bp.route('/departments/<int:department_id>', methods=['GET'])
@patient_required
def get_department_details(department_id):
    """Get department details with list of doctors."""
    department = Department.query.get(department_id)
    if not department:
        return jsonify({'success': False, 'message': 'Department not found'}), 404

    doctors = Doctor.query.filter_by(department_id=department_id, is_active=True).all()

    return jsonify({
        'success': True,
        'department': {
            'id': department.id,
            'name': department.name,
            'description': department.description
        },
        'doctors': [doc.to_dict() for doc in doctors]
    }), 200


@patient_bp.route('/doctors', methods=['GET'])
@patient_required
def search_doctors():
    """Search for doctors by name or filter by department."""
    search = request.args.get('search', '').strip()
    department_id = request.args.get('department_id', type=int)

    query = Doctor.query.filter_by(is_active=True)

    if department_id:
        query = query.filter_by(department_id=department_id)

    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (Doctor.full_name.ilike(search_term)) |
            (Doctor.qualification.ilike(search_term))
        )

    doctors = query.order_by(Doctor.full_name).all()

    return jsonify({
        'success': True,
        'doctors': [doc.to_dict(include_department=True) for doc in doctors]
    }), 200


@patient_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@patient_required
def get_doctor_details(doctor_id):
    """Get doctor details with availability."""
    doctor = Doctor.query.filter_by(id=doctor_id, is_active=True).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor not found'}), 404

    # Get 7-day availability
    today = date.today()
    availability = []

    for i in range(7):
        current_date = today + timedelta(days=i)
        avail = DoctorAvailability.get_for_doctor_and_date(doctor_id, current_date)

        # Get booked slots
        booked_slots = Appointment.get_booked_slots(doctor_id, current_date)
        booked_times = [t.strftime('%H:%M') for t in booked_slots]

        if avail and avail.is_available:
            all_slots = avail.all_slots
            available_slots = [s.strftime('%H:%M') for s in all_slots if s not in booked_slots]

            availability.append({
                'date': current_date.isoformat(),
                'day_name': current_date.strftime('%A'),
                'is_available': True,
                'morning_slots': [s.strftime('%H:%M') for s in avail.morning_slots if s not in booked_slots],
                'evening_slots': [s.strftime('%H:%M') for s in avail.evening_slots if s not in booked_slots],
                'booked_slots': booked_times
            })
        else:
            availability.append({
                'date': current_date.isoformat(),
                'day_name': current_date.strftime('%A'),
                'is_available': False,
                'morning_slots': [],
                'evening_slots': [],
                'booked_slots': booked_times
            })

    return jsonify({
        'success': True,
        'doctor': doctor.to_dict(include_department=True, include_user=True),
        'availability': availability
    }), 200


@patient_bp.route('/doctors/<int:doctor_id>/slots', methods=['GET'])
@patient_required
def get_doctor_slots(doctor_id):
    """Get available slots for a specific date."""
    doctor = Doctor.query.filter_by(id=doctor_id, is_active=True).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor not found'}), 404

    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'success': False, 'message': 'Date is required'}), 400

    try:
        slot_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if slot_date < date.today():
        return jsonify({'success': False, 'message': 'Cannot book past dates'}), 400

    avail = DoctorAvailability.get_for_doctor_and_date(doctor_id, slot_date)
    booked_slots = Appointment.get_booked_slots(doctor_id, slot_date)

    if not avail or not avail.is_available:
        return jsonify({
            'success': True,
            'available': False,
            'slots': []
        }), 200

    available_slots = avail.get_available_slots(booked_slots)

    return jsonify({
        'success': True,
        'available': True,
        'date': slot_date.isoformat(),
        'slots': [s.strftime('%H:%M') for s in available_slots]
    }), 200

