"""
Admin API Routes for the Hospital Management System.
Handles admin dashboard, doctor management, patient management, and appointment oversight.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date

from backend.app.models import db, User, Doctor, Patient, Appointment, Department, Treatment, AppointmentStatusLog
from backend.app.utils.decorators import admin_required, get_current_user_from_request


admin_bp = Blueprint('admin', __name__)


# ============================================================================
# Dashboard Stats
# ============================================================================

@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """
    Get admin dashboard statistics.

    Returns:
        Total counts for doctors, patients, and appointments,
        along with recent activity stats.
    """
    # Total counts
    total_doctors = Doctor.query.filter_by(is_active=True).count()
    total_patients = Patient.query.filter_by(is_active=True).count()
    total_appointments = Appointment.query.count()

    # Today's appointments
    today_appointments = Appointment.query.filter_by(
        appointment_date=date.today()
    ).count()

    # Appointments by status
    booked_count = Appointment.query.filter_by(status='booked').count()
    completed_count = Appointment.query.filter_by(status='completed').count()
    cancelled_count = Appointment.query.filter_by(status='cancelled').count()

    # Recent registrations (last 7 days)
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_patients = Patient.query.filter(Patient.created_at >= week_ago).count()

    # Departments with doctor counts
    departments = Department.get_all_active()
    dept_stats = [
        {
            'id': dept.id,
            'name': dept.name,
            'doctors_count': dept.doctors_count
        }
        for dept in departments
    ]

    return jsonify({
        'success': True,
        'stats': {
            'total_doctors': total_doctors,
            'total_patients': total_patients,
            'total_appointments': total_appointments,
            'today_appointments': today_appointments,
            'appointments_by_status': {
                'booked': booked_count,
                'completed': completed_count,
                'cancelled': cancelled_count
            },
            'new_patients_this_week': new_patients,
            'departments': dept_stats
        }
    }), 200


# ============================================================================
# Doctor Management (CRUD)
# ============================================================================

@admin_bp.route('/doctors', methods=['GET'])
@admin_required
def get_all_doctors():
    """
    Get all doctors with optional filtering.

    Query params:
        search: Search by name or qualification
        department_id: Filter by department
        include_inactive: Include inactive doctors (default: false)
    """
    search = request.args.get('search', '')
    department_id = request.args.get('department_id', type=int)
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

    query = Doctor.query

    if not include_inactive:
        query = query.filter_by(is_active=True)

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
        'doctors': [doc.to_dict(include_user=True) for doc in doctors],
        'total': len(doctors)
    }), 200


@admin_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@admin_required
def get_doctor(doctor_id):
    """Get a specific doctor's details."""
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            'success': False,
            'message': 'Doctor not found'
        }), 404

    return jsonify({
        'success': True,
        'doctor': doctor.to_dict(include_user=True, include_department=True)
    }), 200


@admin_bp.route('/doctors', methods=['POST'])
@admin_required
def create_doctor():
    """
    Create a new doctor profile with user account.

    Required fields:
        username, email, password, full_name, department_id

    Optional fields:
        qualification, experience_years, phone, bio, consultation_fee
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ['username', 'email', 'password', 'full_name', 'department_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'success': False,
                'message': f'{field} is required'
            }), 400

    # Check if username or email already exists
    if User.find_by_username(data['username']):
        return jsonify({
            'success': False,
            'message': 'Username already exists'
        }), 409

    if User.find_by_email(data['email']):
        return jsonify({
            'success': False,
            'message': 'Email already exists'
        }), 409

    # Validate department exists
    department = Department.query.get(data['department_id'])
    if not department:
        return jsonify({
            'success': False,
            'message': 'Department not found'
        }), 404

    try:
        # Create user account
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role='doctor'
        )
        db.session.add(user)
        db.session.flush()  # Get user ID

        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            department_id=data['department_id'],
            full_name=data['full_name'],
            qualification=data.get('qualification'),
            experience_years=data.get('experience_years', 0),
            phone=data.get('phone'),
            bio=data.get('bio'),
            consultation_fee=data.get('consultation_fee', 0.0)
        )
        db.session.add(doctor)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Doctor created successfully',
            'doctor': doctor.to_dict(include_user=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating doctor: {str(e)}'
        }), 500


@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@admin_required
def update_doctor(doctor_id):
    """
    Update doctor profile.

    Updatable fields:
        full_name, department_id, qualification, experience_years,
        phone, bio, consultation_fee, is_active
    """
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            'success': False,
            'message': 'Doctor not found'
        }), 404

    data = request.get_json()

    # Validate department if being updated
    if 'department_id' in data:
        department = Department.query.get(data['department_id'])
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404
        doctor.department_id = data['department_id']

    # Update allowed fields
    updatable_fields = [
        'full_name', 'qualification', 'experience_years',
        'phone', 'bio', 'consultation_fee', 'is_active'
    ]

    for field in updatable_fields:
        if field in data:
            setattr(doctor, field, data[field])

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Doctor updated successfully',
            'doctor': doctor.to_dict(include_user=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating doctor: {str(e)}'
        }), 500


@admin_bp.route('/doctors/<int:doctor_id>/blacklist', methods=['POST'])
@admin_required
def blacklist_doctor(doctor_id):
    """Blacklist a doctor (disable login)."""
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            'success': False,
            'message': 'Doctor not found'
        }), 404

    data = request.get_json() or {}
    blacklist = data.get('blacklist', True)

    doctor.user.is_blacklisted = blacklist
    doctor.is_active = not blacklist

    try:
        db.session.commit()
        action = 'blacklisted' if blacklist else 'unblacklisted'
        return jsonify({
            'success': True,
            'message': f'Doctor {action} successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@admin_required
def delete_doctor(doctor_id):
    """
    Delete a doctor (soft delete - deactivates account).
    Use blacklist for temporary suspension.
    """
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            'success': False,
            'message': 'Doctor not found'
        }), 404

    # Check for upcoming appointments
    upcoming = doctor.appointments.filter(
        Appointment.appointment_date >= date.today(),
        Appointment.status == 'booked'
    ).count()

    if upcoming > 0:
        return jsonify({
            'success': False,
            'message': f'Cannot delete doctor with {upcoming} upcoming appointments. Cancel or reassign them first.'
        }), 400

    try:
        doctor.is_active = False
        doctor.user.is_active = False
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Doctor deactivated successfully'
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

@admin_bp.route('/patients', methods=['GET'])
@admin_required
def get_all_patients():
    """
    Get all patients with optional filtering.

    Query params:
        search: Search by name, phone, or email
        include_inactive: Include inactive patients (default: false)
    """
    search = request.args.get('search', '')
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

    query = Patient.query.join(User)

    if not include_inactive:
        query = query.filter(Patient.is_active == True)

    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (Patient.full_name.ilike(search_term)) |
            (Patient.phone.ilike(search_term)) |
            (User.email.ilike(search_term))
        )

    patients = query.order_by(Patient.full_name).all()

    return jsonify({
        'success': True,
        'patients': [p.to_dict(include_user=True) for p in patients],
        'total': len(patients)
    }), 200


@admin_bp.route('/patients/<int:patient_id>', methods=['GET'])
@admin_required
def get_patient(patient_id):
    """Get a specific patient's details with appointment history."""
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            'success': False,
            'message': 'Patient not found'
        }), 404

    # Get appointment counts
    total_appointments = patient.appointments.count()
    completed_appointments = patient.appointments.filter_by(status='completed').count()

    patient_data = patient.to_dict(include_user=True)
    patient_data['appointment_stats'] = {
        'total': total_appointments,
        'completed': completed_appointments,
        'upcoming': len(patient.upcoming_appointments)
    }

    return jsonify({
        'success': True,
        'patient': patient_data
    }), 200


@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@admin_required
def update_patient(patient_id):
    """Update patient profile (admin can update any field)."""
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            'success': False,
            'message': 'Patient not found'
        }), 404

    data = request.get_json()

    # Update allowed fields
    updatable_fields = [
        'full_name', 'date_of_birth', 'gender', 'phone',
        'address', 'emergency_contact', 'blood_group',
        'medical_history', 'is_active'
    ]

    for field in updatable_fields:
        if field in data:
            value = data[field]
            # Handle date conversion
            if field == 'date_of_birth' and value:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            setattr(patient, field, value)

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Patient updated successfully',
            'patient': patient.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating patient: {str(e)}'
        }), 500


@admin_bp.route('/patients/<int:patient_id>/blacklist', methods=['POST'])
@admin_required
def blacklist_patient(patient_id):
    """Blacklist a patient (disable login)."""
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            'success': False,
            'message': 'Patient not found'
        }), 404

    data = request.get_json() or {}
    blacklist = data.get('blacklist', True)

    patient.user.is_blacklisted = blacklist
    patient.is_active = not blacklist

    try:
        db.session.commit()
        action = 'blacklisted' if blacklist else 'unblacklisted'
        return jsonify({
            'success': True,
            'message': f'Patient {action} successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@admin_bp.route('/patients/<int:patient_id>/appointments', methods=['GET'])
@admin_required
def get_patient_appointments(patient_id):
    """Get complete appointment history for a patient."""
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            'success': False,
            'message': 'Patient not found'
        }), 404

    # Get all appointments with filters
    status = request.args.get('status')
    query = Appointment.query.filter_by(patient_id=patient_id)

    if status:
        query = query.filter_by(status=status)

    appointments = query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time
    ).all()

    return jsonify({
        'success': True,
        'appointments': [
            apt.to_dict(include_doctor=True, include_treatment=True)
            for apt in appointments
        ],
        'total': len(appointments)
    }), 200


@admin_bp.route('/patients/<int:patient_id>/treatments', methods=['GET'])
@admin_required
def get_patient_treatments(patient_id):
    """Get all treatment records for a patient."""
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            'success': False,
            'message': 'Patient not found'
        }), 404

    treatments = Treatment.get_patient_history(patient_id)

    return jsonify({
        'success': True,
        'treatments': [t.to_dict(include_appointment=True) for t in treatments],
        'total': len(treatments)
    }), 200


@admin_bp.route('/treatments/<int:treatment_id>', methods=['GET'])
@admin_required
def get_treatment(treatment_id):
    """Get a specific treatment record."""
    treatment = Treatment.query.get(treatment_id)

    if not treatment:
        return jsonify({
            'success': False,
            'message': 'Treatment not found'
        }), 404

    return jsonify({
        'success': True,
        'treatment': treatment.to_dict(include_appointment=True)
    }), 200


# ============================================================================
# Appointment Management
# ============================================================================

@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def get_all_appointments():
    """
    Get all appointments with filtering options.

    Query params:
        status: Filter by status (booked, completed, cancelled)
        date: Filter by specific date (YYYY-MM-DD)
        date_from: Filter from date
        date_to: Filter to date
        doctor_id: Filter by doctor
        patient_id: Filter by patient
        upcoming: If 'true', show only upcoming appointments
    """
    status = request.args.get('status')
    date_filter = request.args.get('date')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    doctor_id = request.args.get('doctor_id', type=int)
    patient_id = request.args.get('patient_id', type=int)
    upcoming = request.args.get('upcoming', 'false').lower() == 'true'

    query = Appointment.query

    if status:
        query = query.filter_by(status=status)

    if date_filter:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        query = query.filter_by(appointment_date=filter_date)

    if date_from:
        from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        query = query.filter(Appointment.appointment_date >= from_date)

    if date_to:
        to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        query = query.filter(Appointment.appointment_date <= to_date)

    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)

    if patient_id:
        query = query.filter_by(patient_id=patient_id)

    if upcoming:
        query = query.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.status == 'booked'
        )

    appointments = query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time
    ).all()

    return jsonify({
        'success': True,
        'appointments': [
            apt.to_dict(include_patient=True, include_doctor=True)
            for apt in appointments
        ],
        'total': len(appointments)
    }), 200


@admin_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@admin_required
def get_appointment(appointment_id):
    """Get a specific appointment's details."""
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({
            'success': False,
            'message': 'Appointment not found'
        }), 404

    return jsonify({
        'success': True,
        'appointment': appointment.to_dict(
            include_patient=True,
            include_doctor=True,
            include_treatment=True
        )
    }), 200


@admin_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@admin_required
def cancel_appointment(appointment_id):
    """Cancel an appointment (admin action)."""
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({
            'success': False,
            'message': 'Appointment not found'
        }), 404

    if appointment.status != 'booked':
        return jsonify({
            'success': False,
            'message': f'Cannot cancel appointment with status: {appointment.status}'
        }), 400

    data = request.get_json() or {}
    reason = data.get('reason', 'Cancelled by admin')

    try:
        # Log status change
        AppointmentStatusLog.log_status_change(
            appointment=appointment,
            new_status='cancelled',
            changed_by_role='admin',
            changed_by_id=None,
            reason=reason
        )

        appointment.cancel(cancelled_by='admin', reason=reason)
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


@admin_bp.route('/appointments/<int:appointment_id>/status-history', methods=['GET'])
@admin_required
def get_appointment_status_history(appointment_id):
    """Get the status change history for an appointment."""
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({
            'success': False,
            'message': 'Appointment not found'
        }), 404

    logs = AppointmentStatusLog.get_appointment_history(appointment_id)

    return jsonify({
        'success': True,
        'status_history': [log.to_dict() for log in logs]
    }), 200


# ============================================================================
# Department Management
# ============================================================================

@admin_bp.route('/departments', methods=['GET'])
@admin_required
def get_departments():
    """Get all departments with doctor counts."""
    departments = Department.get_all_active()

    return jsonify({
        'success': True,
        'departments': [dept.to_dict() for dept in departments]
    }), 200


@admin_bp.route('/departments', methods=['POST'])
@admin_required
def create_department():
    """Create a new department."""
    data = request.get_json()

    if not data.get('name'):
        return jsonify({
            'success': False,
            'message': 'Department name is required'
        }), 400

    # Check if department already exists
    if Department.find_by_name(data['name']):
        return jsonify({
            'success': False,
            'message': 'Department already exists'
        }), 409

    try:
        department = Department(
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(department)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Department created successfully',
            'department': department.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@admin_bp.route('/departments/<int:dept_id>', methods=['PUT'])
@admin_required
def update_department(dept_id):
    """Update a department."""
    department = Department.query.get(dept_id)

    if not department:
        return jsonify({
            'success': False,
            'message': 'Department not found'
        }), 404

    data = request.get_json()

    if 'name' in data:
        # Check for duplicate name
        existing = Department.find_by_name(data['name'])
        if existing and existing.id != dept_id:
            return jsonify({
                'success': False,
                'message': 'Department name already exists'
            }), 409
        department.name = data['name']

    if 'description' in data:
        department.description = data['description']

    if 'is_active' in data:
        department.is_active = data['is_active']

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Department updated successfully',
            'department': department.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

