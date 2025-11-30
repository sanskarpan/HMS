"""
Patient API routes for the Hospital Management System.
Handles patient dashboard, profile, doctor search, appointment booking, and treatment history.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta, time

from backend.app.models import (
    db, User, Patient, Doctor, Department,
    Appointment, Treatment, DoctorAvailability, AppointmentStatusLog
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


# =============================================================================
# Appointment Booking System
# =============================================================================

@patient_bp.route('/appointments', methods=['GET'])
@patient_required
def get_appointments():
    """Get patient's appointments with filtering."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    status = request.args.get('status')
    period = request.args.get('period')  # upcoming, past, today

    query = Appointment.query.filter_by(patient_id=patient.id)

    today = date.today()

    if status:
        query = query.filter_by(status=status)

    if period == 'upcoming':
        query = query.filter(
            Appointment.appointment_date >= today,
            Appointment.status == 'booked'
        )
    elif period == 'past':
        query = query.filter(
            (Appointment.appointment_date < today) |
            (Appointment.status.in_(['completed', 'cancelled', 'no_show']))
        )
    elif period == 'today':
        query = query.filter(Appointment.appointment_date == today)

    appointments = query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time
    ).all()

    return jsonify({
        'success': True,
        'appointments': [apt.to_dict(include_doctor=True, include_treatment=True) for apt in appointments]
    }), 200


@patient_bp.route('/appointments', methods=['POST'])
@patient_required
def book_appointment():
    """Book a new appointment."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    data = request.get_json()

    # Validate required fields
    doctor_id = data.get('doctor_id')
    appointment_date_str = data.get('appointment_date')
    appointment_time_str = data.get('appointment_time')
    reason = data.get('reason', '')

    if not all([doctor_id, appointment_date_str, appointment_time_str]):
        return jsonify({
            'success': False,
            'message': 'Doctor ID, date, and time are required'
        }), 400

    # Validate doctor
    doctor = Doctor.query.filter_by(id=doctor_id, is_active=True).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor not found'}), 404

    # Parse date and time
    try:
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        appointment_time = datetime.strptime(appointment_time_str, '%H:%M').time()
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Invalid date or time format. Use YYYY-MM-DD and HH:MM'
        }), 400

    # Validate date is not in the past
    if appointment_date < date.today():
        return jsonify({'success': False, 'message': 'Cannot book appointments in the past'}), 400

    # Check doctor availability
    avail = DoctorAvailability.get_for_doctor_and_date(doctor_id, appointment_date)
    if not avail or not avail.is_available:
        return jsonify({
            'success': False,
            'message': 'Doctor is not available on this date'
        }), 400

    # Check if slot is within available hours
    if not avail.is_slot_available(appointment_time):
        return jsonify({
            'success': False,
            'message': 'Selected time is outside available hours'
        }), 400

    # Check for double booking (conflict prevention)
    if not Appointment.check_slot_available(doctor_id, appointment_date, appointment_time):
        return jsonify({
            'success': False,
            'message': 'This time slot is already booked'
        }), 409

    # Check if patient already has an appointment at this time
    existing_patient_apt = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status == 'booked'
    ).first()

    if existing_patient_apt:
        return jsonify({
            'success': False,
            'message': 'You already have an appointment at this time'
        }), 409

    # Create appointment with status logging
    try:
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            department_id=doctor.department_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason,
            duration=avail.slot_duration
        )
        db.session.add(appointment)
        db.session.flush()  # Get the appointment ID

        # Log initial status
        AppointmentStatusLog.log_status_change(
            appointment=appointment,
            new_status='booked',
            changed_by_role='patient',
            changed_by_id=patient.id,
            reason='Appointment created'
        )

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Appointment booked successfully',
            'appointment': appointment.to_dict(include_doctor=True)
        }), 201
    except Exception as e:
        db.session.rollback()
        # Check if it's a unique constraint violation (double booking)
        if 'UNIQUE constraint' in str(e) or 'unique_doctor_appointment_slot' in str(e):
            return jsonify({
                'success': False,
                'message': 'This time slot was just booked by another patient'
            }), 409
        return jsonify({'success': False, 'message': f'Booking failed: {str(e)}'}), 500


@patient_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@patient_required
def get_appointment_details(appointment_id):
    """Get specific appointment details."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        patient_id=patient.id
    ).first()

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

    return jsonify({
        'success': True,
        'appointment': appointment.to_dict(include_doctor=True, include_treatment=True)
    }), 200


@patient_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@patient_required
def cancel_appointment(appointment_id):
    """Cancel an appointment."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        patient_id=patient.id
    ).first()

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

    if not appointment.can_cancel:
        return jsonify({
            'success': False,
            'message': 'This appointment cannot be cancelled'
        }), 400

    data = request.get_json() or {}
    reason = data.get('reason', 'Cancelled by patient')

    try:
        # Log status change before cancelling
        AppointmentStatusLog.log_status_change(
            appointment=appointment,
            new_status='cancelled',
            changed_by_role='patient',
            changed_by_id=patient.id,
            reason=reason
        )

        appointment.cancel(cancelled_by='patient', reason=reason)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Appointment cancelled successfully',
            'appointment': appointment.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@patient_bp.route('/appointments/<int:appointment_id>/reschedule', methods=['POST'])
@patient_required
def reschedule_appointment(appointment_id):
    """Reschedule an appointment."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        patient_id=patient.id
    ).first()

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

    if not appointment.can_reschedule:
        return jsonify({
            'success': False,
            'message': 'This appointment cannot be rescheduled'
        }), 400

    data = request.get_json()
    new_date_str = data.get('appointment_date')
    new_time_str = data.get('appointment_time')

    if not new_date_str or not new_time_str:
        return jsonify({
            'success': False,
            'message': 'New date and time are required'
        }), 400

    try:
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        new_time = datetime.strptime(new_time_str, '%H:%M').time()
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Invalid date or time format'
        }), 400

    if new_date < date.today():
        return jsonify({'success': False, 'message': 'Cannot reschedule to a past date'}), 400

    # Check doctor availability
    avail = DoctorAvailability.get_for_doctor_and_date(appointment.doctor_id, new_date)
    if not avail or not avail.is_available:
        return jsonify({
            'success': False,
            'message': 'Doctor is not available on this date'
        }), 400

    if not avail.is_slot_available(new_time):
        return jsonify({
            'success': False,
            'message': 'Selected time is outside available hours'
        }), 400

    # Check for conflicts
    if not Appointment.check_slot_available(appointment.doctor_id, new_date, new_time):
        return jsonify({
            'success': False,
            'message': 'This time slot is already booked'
        }), 409

    try:
        appointment.reschedule(new_date, new_time)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Appointment rescheduled successfully',
            'appointment': appointment.to_dict(include_doctor=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# =============================================================================
# Appointment History & Treatment View
# =============================================================================

@patient_bp.route('/history', methods=['GET'])
@patient_required
def get_appointment_history():
    """Get complete appointment and treatment history."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    # Get all past/completed appointments with treatments
    appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        (Appointment.appointment_date < date.today()) |
        (Appointment.status.in_(['completed', 'cancelled', 'no_show']))
    ).order_by(Appointment.appointment_date.desc()).all()

    return jsonify({
        'success': True,
        'history': [apt.to_dict(include_doctor=True, include_treatment=True) for apt in appointments]
    }), 200


@patient_bp.route('/treatments', methods=['GET'])
@patient_required
def get_treatments():
    """Get all treatments for the patient."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient.id
    ).order_by(Appointment.appointment_date.desc()).all()

    result = []
    for treatment in treatments:
        data = treatment.to_dict()
        data['appointment'] = treatment.appointment.to_dict(include_doctor=True)
        result.append(data)

    return jsonify({
        'success': True,
        'treatments': result
    }), 200


@patient_bp.route('/treatments/<int:treatment_id>', methods=['GET'])
@patient_required
def get_treatment_details(treatment_id):
    """Get specific treatment details."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    treatment = Treatment.query.join(Appointment).filter(
        Treatment.id == treatment_id,
        Appointment.patient_id == patient.id
    ).first()

    if not treatment:
        return jsonify({'success': False, 'message': 'Treatment not found'}), 404

    result = treatment.to_dict()
    result['appointment'] = treatment.appointment.to_dict(include_doctor=True)

    return jsonify({
        'success': True,
        'treatment': result
    }), 200


# =============================================================================
# CSV Export (Asynchronous with Celery)
# =============================================================================

@patient_bp.route('/export-history', methods=['POST'])
@patient_required
def trigger_export():
    """Trigger asynchronous CSV export of patient's treatment history."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    try:
        from backend.app.tasks.exports import export_patient_history_csv

        # Trigger the async task
        task = export_patient_history_csv.delay(patient.id, notify=True)

        return jsonify({
            'success': True,
            'message': 'Export started. You will be notified when ready.',
            'task_id': task.id
        }), 202
    except Exception as e:
        # If Celery/Redis is not available, do synchronous export
        return _sync_export(patient)


def _sync_export(patient):
    """Fallback synchronous export when Celery is not available."""
    import csv
    import io
    from flask import Response

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'User ID', 'Username', 'Patient Name', 'Consulting Doctor',
        'Department', 'Appointment Date', 'Appointment Time', 'Status',
        'Visit Type', 'Diagnosis', 'Prescription', 'Tests Recommended',
        'Notes', 'Follow-up Date'
    ])

    # Get appointments
    appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id
    ).order_by(Appointment.appointment_date.desc()).all()

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

    # Return CSV response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=patient_history_{patient.id}.csv'
        }
    )


@patient_bp.route('/export-status/<task_id>', methods=['GET'])
@patient_required
def check_export_status(task_id):
    """Check the status of an export task."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    try:
        from backend.app.tasks.exports import get_export_status
        status = get_export_status(task_id)

        return jsonify({
            'success': True,
            'task_id': task_id,
            **status
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error checking status: {str(e)}'
        }), 500


@patient_bp.route('/download-export/<file_id>', methods=['GET'])
@patient_required
def download_export(file_id):
    """Download an exported CSV file."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    try:
        from backend.app.tasks.exports import get_export_file
        from flask import send_file

        filepath, filename = get_export_file(file_id)

        if not filepath or not filename:
            return jsonify({
                'success': False,
                'message': 'Export file not found or expired'
            }), 404

        # Verify the file belongs to this patient
        if f'patient_{patient.id}_' not in filename:
            return jsonify({
                'success': False,
                'message': 'Unauthorized access to export'
            }), 403

        return send_file(
            filepath,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error downloading export: {str(e)}'
        }), 500
