"""
Patient routes - dashboard, profile, doctor search, booking, treatments
"""
import hashlib
import json
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date, timedelta, time

from backend.app.models import (
    db, User, Patient, Doctor, Department,
    Appointment, Treatment, DoctorAvailability, AppointmentStatusLog
)
from backend.app.utils import (
    patient_required,
    get_current_user_from_request
)
from backend.app.services.cache_service import cache, CacheService

patient_bp = Blueprint('patient', __name__)


def get_current_patient():
    """Return patient profile for logged-in user."""
    user = get_current_user_from_request()
    if user and user.patient_profile:
        return user.patient_profile
    return None


@patient_bp.route('/dashboard/stats', methods=['GET'])
@patient_required
def get_dashboard_stats():
    """Fetch patient dashboard stats."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    today = date.today()

    upcoming_count = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date >= today,
        Appointment.status == 'booked'
    ).count()

    completed_count = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == 'completed'
    ).count()

    today_apts = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date == today,
        Appointment.status == 'booked'
    ).order_by(Appointment.appointment_time).all()

    treatment_count = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient.id
    ).count()

    return jsonify({
        'success': True,
        'stats': {
            'upcoming_appointments': upcoming_count,
            'completed_appointments': completed_count,
            'total_treatments': treatment_count,
            'today_appointments': [apt.to_dict(include_doctor=True) for apt in today_apts]
        }
    }), 200


@patient_bp.route('/profile', methods=['GET'])
@patient_required
def get_profile():
    """Fetch patient profile."""
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
    """Update patient profile fields."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    data = request.get_json()

    allowed = ['full_name', 'phone', 'address', 'emergency_contact',
               'blood_group', 'medical_history', 'gender']

    for field in allowed:
        if field in data:
            setattr(patient, field, data[field])

    if 'date_of_birth' in data:
        try:
            if data['date_of_birth']:
                patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            else:
                patient.date_of_birth = None
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format'}), 400

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Profile updated',
            'patient': patient.to_dict(include_user=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@patient_bp.route('/departments', methods=['GET'])
@patient_required
def get_departments():
    """List all departments (cached 30min)."""
    cache_key = 'dept:list:all'
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    departments = Department.query.order_by(Department.name).all()

    result = []
    for dept in departments:
        doc_count = Doctor.query.filter_by(department_id=dept.id, is_active=True).count()
        result.append({
            'id': dept.id,
            'name': dept.name,
            'description': dept.description,
            'doctor_count': doc_count
        })

    response = jsonify({'success': True, 'departments': result}), 200

    cache.set(cache_key, response, timeout=current_app.config.get('CACHE_TTL_STATIC', 1800))
    return response


@patient_bp.route('/departments/<int:department_id>', methods=['GET'])
@patient_required
def get_department_details(department_id):
    """Get department info with doctors (cached 30min)."""
    cache_key = f'dept:{department_id}:details'
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    department = Department.query.get(department_id)
    if not department:
        return jsonify({'success': False, 'message': 'Department not found'}), 404

    doctors = Doctor.query.filter_by(department_id=department_id, is_active=True).all()

    response = jsonify({
        'success': True,
        'department': {
            'id': department.id,
            'name': department.name,
            'description': department.description
        },
        'doctors': [doc.to_dict() for doc in doctors]
    }), 200

    cache.set(cache_key, response, timeout=current_app.config.get('CACHE_TTL_STATIC', 1800))
    return response


@patient_bp.route('/doctors', methods=['GET'])
@patient_required
def search_doctors():
    """Search doctors by name/department (cached 5min)."""
    search = request.args.get('search', '').strip()
    department_id = request.args.get('department_id', type=int)

    params = {'search': search, 'department_id': department_id}
    params_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()[:12]
    cache_key = f'search:doc:{params_hash}'

    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

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

    response = jsonify({
        'success': True,
        'doctors': [doc.to_dict(include_department=True) for doc in doctors]
    }), 200

    cache.set(cache_key, response, timeout=current_app.config.get('CACHE_TTL_SEARCH', 300))
    return response


@patient_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@patient_required
def get_doctor_details(doctor_id):
    """Get doctor details with 7-day availability."""
    doctor = Doctor.query.filter_by(id=doctor_id, is_active=True).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor not found'}), 404

    doc_cache_key = f'doc:{doctor_id}:info'
    doctor_info = cache.get(doc_cache_key)
    if not doctor_info:
        doctor_info = doctor.to_dict(include_department=True, include_user=True)
        cache.set(doc_cache_key, doctor_info, timeout=current_app.config.get('CACHE_TTL_SEMI_STATIC', 600))

    today = date.today()
    availability = []

    for i in range(7):
        current_date = today + timedelta(days=i)
        avail_cache_key = f'avail:{doctor_id}:{current_date.isoformat()}'
        cached_avail = cache.get(avail_cache_key)

        if cached_avail:
            availability.append(cached_avail)
            continue

        avail = DoctorAvailability.get_for_doctor_and_date(doctor_id, current_date)

        booked_slots = Appointment.get_booked_slots(doctor_id, current_date)
        booked_times = [t.strftime('%H:%M') for t in booked_slots]

        if avail and avail.is_available:
            all_slots = avail.all_slots
            available_slots = [s.strftime('%H:%M') for s in all_slots if s not in booked_slots]

            day_avail = {
                'date': current_date.isoformat(),
                'day_name': current_date.strftime('%A'),
                'is_available': True,
                'morning_slots': [s.strftime('%H:%M') for s in avail.morning_slots if s not in booked_slots],
                'evening_slots': [s.strftime('%H:%M') for s in avail.evening_slots if s not in booked_slots],
                'booked_slots': booked_times
            }
        else:
            day_avail = {
                'date': current_date.isoformat(),
                'day_name': current_date.strftime('%A'),
                'is_available': False,
                'morning_slots': [],
                'evening_slots': [],
                'booked_slots': booked_times
            }

        cache.set(avail_cache_key, day_avail, timeout=current_app.config.get('CACHE_TTL_DYNAMIC', 300))
        availability.append(day_avail)

    return jsonify({
        'success': True,
        'doctor': doctor_info,
        'availability': availability
    }), 200


@patient_bp.route('/doctors/<int:doctor_id>/slots', methods=['GET'])
@patient_required
def get_doctor_slots(doctor_id):
    """Get available slots for date (cached 5min)."""
    doctor = Doctor.query.filter_by(id=doctor_id, is_active=True).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor not found'}), 404

    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'success': False, 'message': 'Date required'}), 400

    try:
        slot_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format'}), 400

    if slot_date < date.today():
        return jsonify({'success': False, 'message': 'Cannot book past dates'}), 400

    cache_key = f'slots:{doctor_id}:{slot_date.isoformat()}'
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    avail = DoctorAvailability.get_for_doctor_and_date(doctor_id, slot_date)
    booked_slots = Appointment.get_booked_slots(doctor_id, slot_date)

    if not avail or not avail.is_available:
        response = jsonify({
            'success': True,
            'available': False,
            'slots': []
        }), 200
        cache.set(cache_key, response, timeout=current_app.config.get('CACHE_TTL_DYNAMIC', 300))
        return response

    available_slots = avail.get_available_slots(booked_slots)

    response = jsonify({
        'success': True,
        'available': True,
        'date': slot_date.isoformat(),
        'slots': [s.strftime('%H:%M') for s in available_slots]
    }), 200

    cache.set(cache_key, response, timeout=current_app.config.get('CACHE_TTL_DYNAMIC', 300))
    return response


@patient_bp.route('/appointments', methods=['GET'])
@patient_required
def get_appointments():
    """List patient appointments with filters."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    status = request.args.get('status')
    period = request.args.get('period')

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

    doctor_id = data.get('doctor_id')
    apt_date_str = data.get('appointment_date')
    apt_time_str = data.get('appointment_time')
    reason = data.get('reason', '')

    if not all([doctor_id, apt_date_str, apt_time_str]):
        return jsonify({'success': False, 'message': 'Doctor, date and time required'}), 400

    doctor = Doctor.query.filter_by(id=doctor_id, is_active=True).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor not found'}), 404

    try:
        apt_date = datetime.strptime(apt_date_str, '%Y-%m-%d').date()
        apt_time = datetime.strptime(apt_time_str, '%H:%M').time()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date/time format'}), 400

    if apt_date < date.today():
        return jsonify({'success': False, 'message': 'Cannot book past dates'}), 400

    avail = DoctorAvailability.get_for_doctor_and_date(doctor_id, apt_date)
    if not avail or not avail.is_available:
        return jsonify({'success': False, 'message': 'Doctor unavailable on this date'}), 400

    if not avail.is_slot_available(apt_time):
        return jsonify({'success': False, 'message': 'Time outside available hours'}), 400

    if not Appointment.check_slot_available(doctor_id, apt_date, apt_time):
        return jsonify({'success': False, 'message': 'Slot already booked'}), 409

    existing = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date == apt_date,
        Appointment.appointment_time == apt_time,
        Appointment.status == 'booked'
    ).first()

    if existing:
        return jsonify({'success': False, 'message': 'You already have an appointment at this time'}), 409

    try:
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            department_id=doctor.department_id,
            appointment_date=apt_date,
            appointment_time=apt_time,
            reason=reason,
            duration=avail.slot_duration
        )
        db.session.add(appointment)
        db.session.flush()

        AppointmentStatusLog.log_status_change(
            appointment=appointment,
            new_status='booked',
            changed_by_role='patient',
            changed_by_id=patient.id,
            reason='Appointment created'
        )

        db.session.commit()

        CacheService.invalidate_availability_cache(doctor_id, apt_date.isoformat())
        cache.delete(f'slots:{doctor_id}:{apt_date.isoformat()}')
        cache.delete(f'avail:{doctor_id}:{apt_date.isoformat()}')
        CacheService.invalidate_dashboard_cache('patient', patient.id)
        CacheService.invalidate_dashboard_cache('doctor', doctor_id)

        return jsonify({
            'success': True,
            'message': 'Appointment booked',
            'appointment': appointment.to_dict(include_doctor=True)
        }), 201
    except Exception as e:
        db.session.rollback()
        if 'UNIQUE constraint' in str(e) or 'unique_doctor_appointment_slot' in str(e):
            return jsonify({'success': False, 'message': 'Slot just booked by another patient'}), 409
        return jsonify({'success': False, 'message': f'Booking failed: {str(e)}'}), 500


@patient_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@patient_required
def get_appointment_details(appointment_id):
    """View single appointment."""
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
    """Cancel booked appointment."""
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
        return jsonify({'success': False, 'message': 'Cannot cancel this appointment'}), 400

    data = request.get_json() or {}
    reason = data.get('reason', 'Cancelled by patient')

    try:
        AppointmentStatusLog.log_status_change(
            appointment=appointment,
            new_status='cancelled',
            changed_by_role='patient',
            changed_by_id=patient.id,
            reason=reason
        )

        appointment.cancel(cancelled_by='patient', reason=reason)
        db.session.commit()

        apt_date = appointment.appointment_date.isoformat()
        CacheService.invalidate_availability_cache(appointment.doctor_id, apt_date)
        cache.delete(f'slots:{appointment.doctor_id}:{apt_date}')
        cache.delete(f'avail:{appointment.doctor_id}:{apt_date}')
        CacheService.invalidate_dashboard_cache('patient', patient.id)
        CacheService.invalidate_dashboard_cache('doctor', appointment.doctor_id)

        return jsonify({
            'success': True,
            'message': 'Appointment cancelled',
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
        return jsonify({'success': False, 'message': 'Cannot reschedule this appointment'}), 400

    data = request.get_json()
    new_date_str = data.get('appointment_date')
    new_time_str = data.get('appointment_time')

    if not new_date_str or not new_time_str:
        return jsonify({'success': False, 'message': 'New date and time required'}), 400

    try:
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        new_time = datetime.strptime(new_time_str, '%H:%M').time()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date/time format'}), 400

    if new_date < date.today():
        return jsonify({'success': False, 'message': 'Cannot reschedule to past date'}), 400

    avail = DoctorAvailability.get_for_doctor_and_date(appointment.doctor_id, new_date)
    if not avail or not avail.is_available:
        return jsonify({'success': False, 'message': 'Doctor unavailable on this date'}), 400

    if not avail.is_slot_available(new_time):
        return jsonify({'success': False, 'message': 'Time outside available hours'}), 400

    if not Appointment.check_slot_available(appointment.doctor_id, new_date, new_time):
        return jsonify({'success': False, 'message': 'Slot already booked'}), 409

    try:
        appointment.reschedule(new_date, new_time)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Appointment rescheduled',
            'appointment': appointment.to_dict(include_doctor=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@patient_bp.route('/history', methods=['GET'])
@patient_required
def get_appointment_history():
    """Get past appointments."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

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
    """List all treatments."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient.id
    ).order_by(Appointment.appointment_date.desc()).all()

    result = []
    for t in treatments:
        data = t.to_dict()
        data['appointment'] = t.appointment.to_dict(include_doctor=True)
        result.append(data)

    return jsonify({'success': True, 'treatments': result}), 200


@patient_bp.route('/treatments/<int:treatment_id>', methods=['GET'])
@patient_required
def get_treatment_details(treatment_id):
    """View treatment by ID."""
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

    return jsonify({'success': True, 'treatment': result}), 200


@patient_bp.route('/export-history', methods=['POST'])
@patient_required
def trigger_export():
    """Start async CSV export of treatment history."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    try:
        from backend.app.tasks.exports import export_patient_history_csv

        task = export_patient_history_csv.delay(patient.id, notify=True)

        return jsonify({
            'success': True,
            'message': 'Export started',
            'task_id': task.id
        }), 202
    except Exception as e:
        return _sync_export(patient)


def _sync_export(patient):
    """Fallback sync export if Celery unavailable."""
    import csv
    import io
    from flask import Response

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'User ID', 'Username', 'Patient Name', 'Consulting Doctor',
        'Department', 'Appointment Date', 'Appointment Time', 'Status',
        'Visit Type', 'Diagnosis', 'Prescription', 'Tests Recommended',
        'Notes', 'Follow-up Date'
    ])

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
    """Check export task status."""
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
        return jsonify({'success': False, 'message': f'Status check failed: {str(e)}'}), 500


@patient_bp.route('/download-export/<file_id>', methods=['GET'])
@patient_required
def download_export(file_id):
    """Download exported CSV."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    try:
        from backend.app.tasks.exports import get_export_file
        from flask import send_file

        filepath, filename = get_export_file(file_id)

        if not filepath or not filename:
            return jsonify({'success': False, 'message': 'Export file not found'}), 404

        if f'patient_{patient.id}_' not in filename:
            return jsonify({'success': False, 'message': 'Access denied'}), 403

        return send_file(
            filepath,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'success': False, 'message': f'Download failed: {str(e)}'}), 500
