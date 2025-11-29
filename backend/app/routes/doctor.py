"""
Doctor API Routes for the Hospital Management System.
Handles doctor dashboard, appointments, patients, treatments, and availability.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, time, timedelta

from backend.app.models import (
    db, User, Doctor, Patient, Appointment, Treatment, DoctorAvailability, AppointmentStatusLog
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


# ============================================================================
# Appointments Management
# ============================================================================

@doctor_bp.route('/appointments', methods=['GET'])
@doctor_required
def get_appointments():
    """
    Get doctor's appointments with filtering options.

    Query params:
        date: Specific date (YYYY-MM-DD)
        status: Filter by status (booked, completed, cancelled)
        upcoming: If 'true', show only upcoming appointments
        period: 'today', 'week', or 'month'
    """
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    date_filter = request.args.get('date')
    status = request.args.get('status')
    upcoming = request.args.get('upcoming', 'false').lower() == 'true'
    period = request.args.get('period')

    query = Appointment.query.filter(Appointment.doctor_id == doctor.id)

    if date_filter:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        query = query.filter(Appointment.appointment_date == filter_date)

    if status:
        query = query.filter(Appointment.status == status)

    if upcoming:
        query = query.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.status == 'booked'
        )

    if period == 'today':
        query = query.filter(Appointment.appointment_date == date.today())
    elif period == 'week':
        week_end = date.today() + timedelta(days=7)
        query = query.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.appointment_date < week_end
        )
    elif period == 'month':
        month_end = date.today() + timedelta(days=30)
        query = query.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.appointment_date < month_end
        )

    appointments = query.order_by(
        Appointment.appointment_date,
        Appointment.appointment_time
    ).all()

    return jsonify({
        'success': True,
        'appointments': [
            apt.to_dict(include_patient=True, include_treatment=True)
            for apt in appointments
        ],
        'total': len(appointments)
    }), 200


@doctor_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@doctor_required
def get_appointment(appointment_id):
    """Get a specific appointment's details."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        doctor_id=doctor.id
    ).first()

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

    return jsonify({
        'success': True,
        'appointment': appointment.to_dict(
            include_patient=True,
            include_treatment=True
        )
    }), 200


@doctor_bp.route('/appointments/<int:appointment_id>/complete', methods=['POST'])
@doctor_required
def complete_appointment(appointment_id):
    """
    Mark an appointment as completed and add treatment details.

    Required fields:
        diagnosis: Medical diagnosis

    Optional fields:
        prescription, notes, tests_recommended, follow_up_date, visit_type
    """
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        doctor_id=doctor.id
    ).first()

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

    if appointment.status != 'booked':
        return jsonify({
            'success': False,
            'message': f'Cannot complete appointment with status: {appointment.status}'
        }), 400

    data = request.get_json()

    if not data.get('diagnosis'):
        return jsonify({
            'success': False,
            'message': 'Diagnosis is required to complete appointment'
        }), 400

    try:
        # Log status change
        AppointmentStatusLog.log_status_change(
            appointment=appointment,
            new_status='completed',
            changed_by_role='doctor',
            changed_by_id=doctor.id,
            reason=f'Diagnosis: {data["diagnosis"][:50]}...' if len(data['diagnosis']) > 50 else f'Diagnosis: {data["diagnosis"]}'
        )

        # Mark appointment as completed
        appointment.complete()

        # Create treatment record
        follow_up_date = None
        if data.get('follow_up_date'):
            follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()

        treatment = Treatment(
            appointment_id=appointment.id,
            diagnosis=data['diagnosis'],
            prescription=data.get('prescription'),
            notes=data.get('notes'),
            tests_recommended=data.get('tests_recommended'),
            follow_up_date=follow_up_date,
            follow_up_notes=data.get('follow_up_notes'),
            visit_type=data.get('visit_type', 'in-person')
        )
        db.session.add(treatment)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Appointment completed successfully',
            'treatment': treatment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error completing appointment: {str(e)}'
        }), 500


@doctor_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@doctor_required
def cancel_appointment(appointment_id):
    """Cancel an appointment."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        doctor_id=doctor.id
    ).first()

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

    if appointment.status != 'booked':
        return jsonify({
            'success': False,
            'message': f'Cannot cancel appointment with status: {appointment.status}'
        }), 400

    data = request.get_json() or {}
    reason = data.get('reason', 'Cancelled by doctor')

    try:
        # Log status change
        AppointmentStatusLog.log_status_change(
            appointment=appointment,
            new_status='cancelled',
            changed_by_role='doctor',
            changed_by_id=doctor.id,
            reason=reason
        )

        appointment.cancel(cancelled_by='doctor', reason=reason)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Appointment cancelled successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@doctor_bp.route('/appointments/<int:appointment_id>/no-show', methods=['POST'])
@doctor_required
def mark_no_show(appointment_id):
    """Mark an appointment as no-show."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        doctor_id=doctor.id
    ).first()

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

    try:
        # Log status change
        AppointmentStatusLog.log_status_change(
            appointment=appointment,
            new_status='no_show',
            changed_by_role='doctor',
            changed_by_id=doctor.id,
            reason='Patient did not attend'
        )

        appointment.mark_no_show()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Appointment marked as no-show'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


# ============================================================================
# Patient Management
# ============================================================================

@doctor_bp.route('/patients', methods=['GET'])
@doctor_required
def get_patients():
    """
    Get list of patients assigned to this doctor.
    These are patients who have had appointments with this doctor.
    """
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    search = request.args.get('search', '')

    # Get unique patients who have appointments with this doctor
    patient_ids = db.session.query(Appointment.patient_id).filter(
        Appointment.doctor_id == doctor.id
    ).distinct().all()

    patient_ids = [p[0] for p in patient_ids]

    query = Patient.query.filter(Patient.id.in_(patient_ids))

    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (Patient.full_name.ilike(search_term)) |
            (Patient.phone.ilike(search_term))
        )

    patients = query.order_by(Patient.full_name).all()

    # Add appointment count for each patient
    result = []
    for patient in patients:
        patient_data = patient.to_dict()
        patient_data['appointment_count'] = Appointment.query.filter_by(
            patient_id=patient.id,
            doctor_id=doctor.id
        ).count()
        result.append(patient_data)

    return jsonify({
        'success': True,
        'patients': result,
        'total': len(result)
    }), 200


@doctor_bp.route('/patients/<int:patient_id>', methods=['GET'])
@doctor_required
def get_patient_details(patient_id):
    """Get a specific patient's details and appointment history with this doctor."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    # Verify patient has had appointments with this doctor
    has_appointment = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).first()

    if not has_appointment:
        return jsonify({
            'success': False,
            'message': 'Patient not found in your records'
        }), 404

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'success': False, 'message': 'Patient not found'}), 404

    # Get appointment history with this doctor
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).order_by(Appointment.appointment_date.desc()).all()

    patient_data = patient.to_dict()
    patient_data['appointments'] = [
        apt.to_dict(include_treatment=True) for apt in appointments
    ]

    return jsonify({
        'success': True,
        'patient': patient_data
    }), 200


@doctor_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@doctor_required
def get_patient_history(patient_id):
    """Get full treatment history for a patient (all doctors)."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    # Verify patient has had appointments with this doctor
    has_appointment = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).first()

    if not has_appointment:
        return jsonify({
            'success': False,
            'message': 'Patient not found in your records'
        }), 404

    # Get all treatments for this patient
    treatments = Treatment.get_patient_history(patient_id)

    return jsonify({
        'success': True,
        'history': [t.to_dict(include_appointment=True) for t in treatments],
        'total': len(treatments)
    }), 200


# ============================================================================
# Treatment Management
# ============================================================================

@doctor_bp.route('/treatments/<int:treatment_id>', methods=['GET'])
@doctor_required
def get_treatment(treatment_id):
    """Get a specific treatment record."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    treatment = Treatment.query.join(Appointment).filter(
        Treatment.id == treatment_id,
        Appointment.doctor_id == doctor.id
    ).first()

    if not treatment:
        return jsonify({'success': False, 'message': 'Treatment not found'}), 404

    return jsonify({
        'success': True,
        'treatment': treatment.to_dict(include_appointment=True)
    }), 200


@doctor_bp.route('/treatments/<int:treatment_id>', methods=['PUT'])
@doctor_required
def update_treatment(treatment_id):
    """Update a treatment record (only by the treating doctor)."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    treatment = Treatment.query.join(Appointment).filter(
        Treatment.id == treatment_id,
        Appointment.doctor_id == doctor.id
    ).first()

    if not treatment:
        return jsonify({'success': False, 'message': 'Treatment not found'}), 404

    data = request.get_json()

    # Update allowed fields
    if 'diagnosis' in data:
        treatment.diagnosis = data['diagnosis']
    if 'prescription' in data:
        treatment.prescription = data['prescription']
    if 'notes' in data:
        treatment.notes = data['notes']
    if 'tests_recommended' in data:
        treatment.tests_recommended = data['tests_recommended']
    if 'follow_up_date' in data:
        if data['follow_up_date']:
            treatment.follow_up_date = datetime.strptime(
                data['follow_up_date'], '%Y-%m-%d'
            ).date()
        else:
            treatment.follow_up_date = None
    if 'follow_up_notes' in data:
        treatment.follow_up_notes = data['follow_up_notes']
    if 'visit_type' in data:
        treatment.visit_type = data['visit_type']

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Treatment updated successfully',
            'treatment': treatment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


# ============================================================================
# Availability Management
# ============================================================================

@doctor_bp.route('/availability', methods=['GET'])
@doctor_required
def get_availability():
    """Get doctor's availability for the next 7 days."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    availability = DoctorAvailability.get_week_availability(doctor.id)

    # Create a full 7-day response, filling in missing days with default
    today = date.today()
    result = []

    for i in range(7):
        day = today + timedelta(days=i)
        existing = next((a for a in availability if a.date == day), None)

        if existing:
            result.append(existing.to_dict(include_slots=True))
        else:
            # Default: not yet set
            result.append({
                'date': day.isoformat(),
                'is_available': False,
                'is_set': False,
                'start_time_morning': None,
                'end_time_morning': None,
                'start_time_evening': None,
                'end_time_evening': None,
                'slot_duration': 30,
                'morning_slots': [],
                'evening_slots': []
            })

    return jsonify({
        'success': True,
        'availability': result
    }), 200


@doctor_bp.route('/availability', methods=['POST'])
@doctor_required
def set_availability():
    """
    Set availability for a specific date.

    Required:
        date: Date in YYYY-MM-DD format

    Optional:
        is_available: Boolean (default: true)
        start_time_morning: HH:MM format
        end_time_morning: HH:MM format
        start_time_evening: HH:MM format
        end_time_evening: HH:MM format
        slot_duration: Integer minutes (default: 30)
    """
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    data = request.get_json()

    if not data.get('date'):
        return jsonify({
            'success': False,
            'message': 'Date is required'
        }), 400

    try:
        availability_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Invalid date format. Use YYYY-MM-DD'
        }), 400

    # Parse time values
    def parse_time(time_str):
        if not time_str:
            return None
        return datetime.strptime(time_str, '%H:%M').time()

    try:
        morning_start = parse_time(data.get('start_time_morning'))
        morning_end = parse_time(data.get('end_time_morning'))
        evening_start = parse_time(data.get('start_time_evening'))
        evening_end = parse_time(data.get('end_time_evening'))

        availability = DoctorAvailability.set_availability(
            doctor_id=doctor.id,
            availability_date=availability_date,
            morning_start=morning_start,
            morning_end=morning_end,
            evening_start=evening_start,
            evening_end=evening_end,
            is_available=data.get('is_available', True),
            slot_duration=data.get('slot_duration', 30)
        )

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Availability set successfully',
            'availability': availability.to_dict(include_slots=True)
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@doctor_bp.route('/availability/bulk', methods=['POST'])
@doctor_required
def set_bulk_availability():
    """
    Set availability for multiple dates at once.

    Request body:
        slots: Array of availability objects, each containing:
            - date
            - is_available
            - start_time_morning, end_time_morning
            - start_time_evening, end_time_evening
            - slot_duration
    """
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    data = request.get_json()
    slots = data.get('slots', [])

    if not slots:
        return jsonify({
            'success': False,
            'message': 'No availability slots provided'
        }), 400

    def parse_time(time_str):
        if not time_str:
            return None
        return datetime.strptime(time_str, '%H:%M').time()

    results = []
    errors = []

    for slot in slots:
        try:
            availability_date = datetime.strptime(slot['date'], '%Y-%m-%d').date()

            availability = DoctorAvailability.set_availability(
                doctor_id=doctor.id,
                availability_date=availability_date,
                morning_start=parse_time(slot.get('start_time_morning')),
                morning_end=parse_time(slot.get('end_time_morning')),
                evening_start=parse_time(slot.get('start_time_evening')),
                evening_end=parse_time(slot.get('end_time_evening')),
                is_available=slot.get('is_available', True),
                slot_duration=slot.get('slot_duration', 30)
            )
            results.append(availability.to_dict())

        except Exception as e:
            errors.append({
                'date': slot.get('date'),
                'error': str(e)
            })

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error saving availability: {str(e)}'
        }), 500

    return jsonify({
        'success': True,
        'message': f'Set availability for {len(results)} days',
        'results': results,
        'errors': errors if errors else None
    }), 200


# ============================================================================
# Profile
# ============================================================================

@doctor_bp.route('/profile', methods=['GET'])
@doctor_required
def get_profile():
    """Get current doctor's profile."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    return jsonify({
        'success': True,
        'doctor': doctor.to_dict(include_user=True, include_department=True)
    }), 200


@doctor_bp.route('/profile', methods=['PUT'])
@doctor_required
def update_profile():
    """Update doctor's profile (limited fields)."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    data = request.get_json()

    # Doctors can only update certain fields
    updatable_fields = ['phone', 'bio', 'consultation_fee']

    for field in updatable_fields:
        if field in data:
            setattr(doctor, field, data[field])

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'doctor': doctor.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
