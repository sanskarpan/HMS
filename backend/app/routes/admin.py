"""
Admin routes - dashboard stats, doctor/patient/appointment management
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date

from backend.app.models import db, User, Doctor, Patient, Appointment, Department, Treatment, AppointmentStatusLog
from backend.app.utils.decorators import admin_required
from backend.app.services.cache_service import cache, CacheService


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Fetch overall system stats for admin dashboard (cached 2min)."""
    cache_key = 'dash:admin:stats'
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    total_doctors = Doctor.query.filter_by(is_active=True).count()
    total_patients = Patient.query.filter_by(is_active=True).count()
    total_appointments = Appointment.query.count()

    today_appointments = Appointment.query.filter_by(
        appointment_date=date.today()
    ).count()

    booked_count = Appointment.query.filter_by(status='booked').count()
    completed_count = Appointment.query.filter_by(status='completed').count()
    cancelled_count = Appointment.query.filter_by(status='cancelled').count()

    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_patients = Patient.query.filter(Patient.created_at >= week_ago).count()

    departments = Department.get_all_active()
    dept_stats = [
        {
            'id': dept.id,
            'name': dept.name,
            'doctors_count': dept.doctors_count
        }
        for dept in departments
    ]

    response = jsonify({
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

    cache.set(cache_key, response, timeout=current_app.config.get('CACHE_TTL_REALTIME', 120))
    return response


@admin_bp.route('/doctors', methods=['GET'])
@admin_required
def get_all_doctors():
    """List doctors with optional search/filter."""
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
    """Fetch single doctor by ID."""
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor not found'}), 404

    return jsonify({
        'success': True,
        'doctor': doctor.to_dict(include_user=True, include_department=True)
    }), 200


@admin_bp.route('/doctors', methods=['POST'])
@admin_required
def create_doctor():
    """Add new doctor with login credentials."""
    data = request.get_json()

    required_fields = ['username', 'email', 'password', 'full_name', 'department_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400

    if User.find_by_username(data['username']):
        return jsonify({'success': False, 'message': 'Username already exists'}), 409

    if User.find_by_email(data['email']):
        return jsonify({'success': False, 'message': 'Email already exists'}), 409

    department = Department.query.get(data['department_id'])
    if not department:
        return jsonify({'success': False, 'message': 'Department not found'}), 404

    try:
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role='doctor'
        )
        db.session.add(user)
        db.session.flush()

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
        return jsonify({'success': False, 'message': f'Failed to create doctor: {str(e)}'}), 500


@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@admin_required
def update_doctor(doctor_id):
    """Modify doctor details."""
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor not found'}), 404

    data = request.get_json()

    if 'department_id' in data:
        department = Department.query.get(data['department_id'])
        if not department:
            return jsonify({'success': False, 'message': 'Department not found'}), 404
        doctor.department_id = data['department_id']

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
            'message': 'Doctor updated',
            'doctor': doctor.to_dict(include_user=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Update failed: {str(e)}'}), 500


@admin_bp.route('/doctors/<int:doctor_id>/blacklist', methods=['POST'])
@admin_required
def blacklist_doctor(doctor_id):
    """Block or unblock doctor login."""
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor not found'}), 404

    data = request.get_json() or {}
    blacklist = data.get('blacklist', True)

    doctor.user.is_blacklisted = blacklist
    doctor.is_active = not blacklist

    try:
        db.session.commit()
        action = 'blacklisted' if blacklist else 'unblacklisted'
        return jsonify({'success': True, 'message': f'Doctor {action}'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@admin_required
def delete_doctor(doctor_id):
    """Deactivate doctor account (soft delete)."""
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor not found'}), 404

    upcoming = doctor.appointments.filter(
        Appointment.appointment_date >= date.today(),
        Appointment.status == 'booked'
    ).count()

    if upcoming > 0:
        return jsonify({
            'success': False,
            'message': f'Cannot delete - {upcoming} upcoming appointments exist'
        }), 400

    try:
        doctor.is_active = False
        doctor.user.is_active = False
        db.session.commit()

        return jsonify({'success': True, 'message': 'Doctor deactivated'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/patients', methods=['GET'])
@admin_required
def get_all_patients():
    """List all patients with optional search."""
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
    """Get patient details with appointment stats."""
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({'success': False, 'message': 'Patient not found'}), 404

    total_appointments = patient.appointments.count()
    completed_appointments = patient.appointments.filter_by(status='completed').count()

    patient_data = patient.to_dict(include_user=True)
    patient_data['appointment_stats'] = {
        'total': total_appointments,
        'completed': completed_appointments,
        'upcoming': len(patient.upcoming_appointments)
    }

    return jsonify({'success': True, 'patient': patient_data}), 200


@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@admin_required
def update_patient(patient_id):
    """Modify patient profile."""
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({'success': False, 'message': 'Patient not found'}), 404

    data = request.get_json()

    updatable_fields = [
        'full_name', 'date_of_birth', 'gender', 'phone',
        'address', 'emergency_contact', 'blood_group',
        'medical_history', 'is_active'
    ]

    for field in updatable_fields:
        if field in data:
            value = data[field]
            if field == 'date_of_birth' and value:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            setattr(patient, field, value)

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Patient updated',
            'patient': patient.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Update failed: {str(e)}'}), 500


@admin_bp.route('/patients/<int:patient_id>/blacklist', methods=['POST'])
@admin_required
def blacklist_patient(patient_id):
    """Block/unblock patient login."""
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({'success': False, 'message': 'Patient not found'}), 404

    data = request.get_json() or {}
    blacklist = data.get('blacklist', True)

    patient.user.is_blacklisted = blacklist
    patient.is_active = not blacklist

    try:
        db.session.commit()
        action = 'blacklisted' if blacklist else 'unblacklisted'
        return jsonify({'success': True, 'message': f'Patient {action}'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/patients/<int:patient_id>/appointments', methods=['GET'])
@admin_required
def get_patient_appointments(patient_id):
    """Fetch patient's appointment history."""
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({'success': False, 'message': 'Patient not found'}), 404

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
    """List treatments for a patient."""
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({'success': False, 'message': 'Patient not found'}), 404

    treatments = Treatment.get_patient_history(patient_id)

    return jsonify({
        'success': True,
        'treatments': [t.to_dict(include_appointment=True) for t in treatments],
        'total': len(treatments)
    }), 200


@admin_bp.route('/treatments/<int:treatment_id>', methods=['GET'])
@admin_required
def get_treatment(treatment_id):
    """View specific treatment record."""
    treatment = Treatment.query.get(treatment_id)

    if not treatment:
        return jsonify({'success': False, 'message': 'Treatment not found'}), 404

    return jsonify({
        'success': True,
        'treatment': treatment.to_dict(include_appointment=True)
    }), 200


@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def get_all_appointments():
    """List appointments with filters."""
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
    """View appointment details."""
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

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
    """Cancel appointment as admin."""
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

    if appointment.status != 'booked':
        return jsonify({
            'success': False,
            'message': f'Cannot cancel - status is {appointment.status}'
        }), 400

    data = request.get_json() or {}
    reason = data.get('reason', 'Cancelled by admin')

    try:
        AppointmentStatusLog.log_status_change(
            appointment=appointment,
            new_status='cancelled',
            changed_by_role='admin',
            changed_by_id=None,
            reason=reason
        )

        appointment.cancel(cancelled_by='admin', reason=reason)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Appointment cancelled'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/appointments/<int:appointment_id>/status-history', methods=['GET'])
@admin_required
def get_appointment_status_history(appointment_id):
    """View status change history for appointment."""
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

    logs = AppointmentStatusLog.get_appointment_history(appointment_id)

    return jsonify({
        'success': True,
        'status_history': [log.to_dict() for log in logs]
    }), 200


@admin_bp.route('/departments', methods=['GET'])
@admin_required
def get_departments():
    """List departments (cached 30min)."""
    cache_key = 'admin:dept:list'
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    departments = Department.get_all_active()

    response = jsonify({
        'success': True,
        'departments': [dept.to_dict() for dept in departments]
    }), 200

    cache.set(cache_key, response, timeout=current_app.config.get('CACHE_TTL_STATIC', 1800))
    return response


@admin_bp.route('/departments', methods=['POST'])
@admin_required
def create_department():
    """Add new department."""
    data = request.get_json()

    if not data.get('name'):
        return jsonify({'success': False, 'message': 'Name required'}), 400

    if Department.find_by_name(data['name']):
        return jsonify({'success': False, 'message': 'Department already exists'}), 409

    try:
        department = Department(
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(department)
        db.session.commit()

        CacheService.invalidate_department_cache()
        cache.delete('admin:dept:list')
        cache.delete('dept:list:all')

        return jsonify({
            'success': True,
            'message': 'Department created',
            'department': department.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/departments/<int:dept_id>', methods=['PUT'])
@admin_required
def update_department(dept_id):
    """Modify department."""
    department = Department.query.get(dept_id)

    if not department:
        return jsonify({'success': False, 'message': 'Department not found'}), 404

    data = request.get_json()

    if 'name' in data:
        existing = Department.find_by_name(data['name'])
        if existing and existing.id != dept_id:
            return jsonify({'success': False, 'message': 'Name already taken'}), 409
        department.name = data['name']

    if 'description' in data:
        department.description = data['description']

    if 'is_active' in data:
        department.is_active = data['is_active']

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Department updated',
            'department': department.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
