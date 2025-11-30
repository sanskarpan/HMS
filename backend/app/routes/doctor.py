"""
Doctor routes - dashboard, appointments, patients, treatments, availability
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta

from backend.app.models import (
    db, User, Doctor, Patient, Appointment, Treatment, DoctorAvailability, AppointmentStatusLog
)
from backend.app.utils.decorators import doctor_required, get_current_user_from_request


doctor_bp = Blueprint('doctor', __name__)


def get_current_doctor():
    """Return doctor profile for logged-in user."""
    user = get_current_user_from_request()
    if user and user.doctor_profile:
        return user.doctor_profile
    return None


@doctor_bp.route('/dashboard/stats', methods=['GET'])
@doctor_required
def get_dashboard_stats():
    """Fetch stats for doctor dashboard."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    today = date.today()
    week_end = today + timedelta(days=7)

    today_apts = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date == today
    ).all()

    week_count = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= today,
        Appointment.appointment_date < week_end,
        Appointment.status == 'booked'
    ).count()

    patient_count = db.session.query(Appointment.patient_id).filter(
        Appointment.doctor_id == doctor.id
    ).distinct().count()

    pending_count = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status == 'booked',
        Appointment.appointment_date >= today
    ).count()

    done_count = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status == 'completed'
    ).count()

    return jsonify({
        'success': True,
        'stats': {
            'today_appointments': len(today_apts),
            'today_appointments_list': [
                apt.to_dict(include_patient=True) for apt in today_apts
            ],
            'week_appointments': week_count,
            'total_patients': patient_count,
            'pending_appointments': pending_count,
            'completed_appointments': done_count
        },
        'doctor': {
            'id': doctor.id,
            'full_name': doctor.full_name,
            'department': doctor.department.name if doctor.department else None
        }
    }), 200


@doctor_bp.route('/appointments', methods=['GET'])
@doctor_required
def get_appointments():
    """List doctor's appointments with filters."""
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
    """View appointment by ID."""
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
    """Mark appointment done and record treatment."""
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
            'message': f'Cannot complete - status is {appointment.status}'
        }), 400

    data = request.get_json()

    if not data.get('diagnosis'):
        return jsonify({'success': False, 'message': 'Diagnosis required'}), 400

    try:
        diag_preview = data['diagnosis'][:50] + '...' if len(data['diagnosis']) > 50 else data['diagnosis']
        AppointmentStatusLog.log_status_change(
            appointment=appointment,
            new_status='completed',
            changed_by_role='doctor',
            changed_by_id=doctor.id,
            reason=f'Diagnosis: {diag_preview}'
        )

        appointment.complete()

        follow_up = None
        if data.get('follow_up_date'):
            follow_up = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()

        treatment = Treatment(
            appointment_id=appointment.id,
            diagnosis=data['diagnosis'],
            prescription=data.get('prescription'),
            notes=data.get('notes'),
            tests_recommended=data.get('tests_recommended'),
            follow_up_date=follow_up,
            follow_up_notes=data.get('follow_up_notes'),
            visit_type=data.get('visit_type', 'in-person')
        )
        db.session.add(treatment)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Appointment completed',
            'treatment': treatment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@doctor_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@doctor_required
def cancel_appointment(appointment_id):
    """Cancel booked appointment."""
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
            'message': f'Cannot cancel - status is {appointment.status}'
        }), 400

    data = request.get_json() or {}
    reason = data.get('reason', 'Cancelled by doctor')

    try:
        AppointmentStatusLog.log_status_change(
            appointment=appointment,
            new_status='cancelled',
            changed_by_role='doctor',
            changed_by_id=doctor.id,
            reason=reason
        )

        appointment.cancel(cancelled_by='doctor', reason=reason)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Appointment cancelled'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@doctor_bp.route('/appointments/<int:appointment_id>/no-show', methods=['POST'])
@doctor_required
def mark_no_show(appointment_id):
    """Mark patient as no-show."""
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
        AppointmentStatusLog.log_status_change(
            appointment=appointment,
            new_status='no_show',
            changed_by_role='doctor',
            changed_by_id=doctor.id,
            reason='Patient did not attend'
        )

        appointment.mark_no_show()
        db.session.commit()

        return jsonify({'success': True, 'message': 'Marked as no-show'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@doctor_bp.route('/patients', methods=['GET'])
@doctor_required
def get_patients():
    """List patients who've had appointments with this doctor."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    search = request.args.get('search', '')

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

    result = []
    for p in patients:
        pdata = p.to_dict()
        pdata['appointment_count'] = Appointment.query.filter_by(
            patient_id=p.id,
            doctor_id=doctor.id
        ).count()
        result.append(pdata)

    return jsonify({
        'success': True,
        'patients': result,
        'total': len(result)
    }), 200


@doctor_bp.route('/patients/<int:patient_id>', methods=['GET'])
@doctor_required
def get_patient_details(patient_id):
    """View patient details and history with this doctor."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    has_apt = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).first()

    if not has_apt:
        return jsonify({'success': False, 'message': 'Patient not in your records'}), 404

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'success': False, 'message': 'Patient not found'}), 404

    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).order_by(Appointment.appointment_date.desc()).all()

    pdata = patient.to_dict()
    pdata['appointments'] = [
        apt.to_dict(include_treatment=True) for apt in appointments
    ]

    return jsonify({'success': True, 'patient': pdata}), 200


@doctor_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@doctor_required
def get_patient_history(patient_id):
    """View full treatment history for a patient."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    has_apt = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).first()

    if not has_apt:
        return jsonify({'success': False, 'message': 'Patient not in your records'}), 404

    treatments = Treatment.get_patient_history(patient_id)

    return jsonify({
        'success': True,
        'history': [t.to_dict(include_appointment=True) for t in treatments],
        'total': len(treatments)
    }), 200


@doctor_bp.route('/treatments/<int:treatment_id>', methods=['GET'])
@doctor_required
def get_treatment(treatment_id):
    """Fetch treatment record by ID."""
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
    """Modify treatment record."""
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
            'message': 'Treatment updated',
            'treatment': treatment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@doctor_bp.route('/availability', methods=['GET'])
@doctor_required
def get_availability():
    """Get 7-day availability schedule."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    avail_list = DoctorAvailability.get_week_availability(doctor.id)

    today = date.today()
    result = []

    for i in range(7):
        day = today + timedelta(days=i)
        existing = next((a for a in avail_list if a.date == day), None)

        if existing:
            result.append(existing.to_dict(include_slots=True))
        else:
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

    return jsonify({'success': True, 'availability': result}), 200


@doctor_bp.route('/availability', methods=['POST'])
@doctor_required
def set_availability():
    """Set availability for a specific date."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    data = request.get_json()

    if not data.get('date'):
        return jsonify({'success': False, 'message': 'Date required'}), 400

    try:
        avail_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format'}), 400

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
            availability_date=avail_date,
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
            'message': 'Availability set',
            'availability': availability.to_dict(include_slots=True)
        }), 200

    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@doctor_bp.route('/availability/bulk', methods=['POST'])
@doctor_required
def set_bulk_availability():
    """Set availability for multiple dates."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    data = request.get_json()
    slots = data.get('slots', [])

    if not slots:
        return jsonify({'success': False, 'message': 'No slots provided'}), 400

    def parse_time(time_str):
        if not time_str:
            return None
        return datetime.strptime(time_str, '%H:%M').time()

    results = []
    errors = []

    for slot in slots:
        try:
            avail_date = datetime.strptime(slot['date'], '%Y-%m-%d').date()

            availability = DoctorAvailability.set_availability(
                doctor_id=doctor.id,
                availability_date=avail_date,
                morning_start=parse_time(slot.get('start_time_morning')),
                morning_end=parse_time(slot.get('end_time_morning')),
                evening_start=parse_time(slot.get('start_time_evening')),
                evening_end=parse_time(slot.get('end_time_evening')),
                is_available=slot.get('is_available', True),
                slot_duration=slot.get('slot_duration', 30)
            )
            results.append(availability.to_dict())

        except Exception as e:
            errors.append({'date': slot.get('date'), 'error': str(e)})

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Save error: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'message': f'Set availability for {len(results)} days',
        'results': results,
        'errors': errors if errors else None
    }), 200


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
    """Update profile fields."""
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    data = request.get_json()

    allowed = ['phone', 'bio', 'consultation_fee']

    for field in allowed:
        if field in data:
            setattr(doctor, field, data[field])

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Profile updated',
            'doctor': doctor.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@doctor_bp.route('/charts/weekly-appointments', methods=['GET'])
@doctor_required
def get_weekly_appointments_chart():
    """Get appointment counts for past 4 weeks for line chart."""
    from sqlalchemy import func

    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    weeks = request.args.get('weeks', 4, type=int)
    end_date = date.today()
    start_date = end_date - timedelta(days=weeks * 7)

    results = db.session.query(
        Appointment.appointment_date,
        func.count(Appointment.id)
    ).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    ).group_by(
        Appointment.appointment_date
    ).order_by(
        Appointment.appointment_date
    ).all()

    date_counts = {r[0]: r[1] for r in results}

    labels = []
    data = []
    current = start_date
    while current <= end_date:
        labels.append(current.strftime('%Y-%m-%d'))
        data.append(date_counts.get(current, 0))
        current += timedelta(days=1)

    return jsonify({
        'success': True,
        'chart_data': {
            'labels': labels,
            'datasets': [{
                'label': 'Appointments',
                'data': data,
                'borderColor': '#36A2EB',
                'fill': False
            }]
        }
    }), 200


@doctor_bp.route('/charts/appointments-by-status', methods=['GET'])
@doctor_required
def get_doctor_appointments_by_status():
    """Get appointment status distribution for doughnut chart."""
    from sqlalchemy import func

    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    results = db.session.query(
        Appointment.status,
        func.count(Appointment.id)
    ).filter(
        Appointment.doctor_id == doctor.id
    ).group_by(
        Appointment.status
    ).all()

    labels = [r[0].title() for r in results]
    data = [r[1] for r in results]

    status_colors = {
        'Booked': '#36A2EB',
        'Completed': '#4BC0C0',
        'Cancelled': '#FF6384',
        'No_show': '#FFCE56'
    }

    colors = [status_colors.get(label, '#9966FF') for label in labels]

    return jsonify({
        'success': True,
        'chart_data': {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors
            }]
        }
    }), 200


@doctor_bp.route('/charts/patient-visits', methods=['GET'])
@doctor_required
def get_patient_visits_chart():
    """Get top patients by visit count for bar chart."""
    from sqlalchemy import func

    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    results = db.session.query(
        Patient.full_name,
        func.count(Appointment.id)
    ).join(
        Appointment, Patient.id == Appointment.patient_id
    ).filter(
        Appointment.doctor_id == doctor.id
    ).group_by(
        Patient.id, Patient.full_name
    ).order_by(
        func.count(Appointment.id).desc()
    ).limit(10).all()

    labels = [r[0] for r in results]
    data = [r[1] for r in results]

    return jsonify({
        'success': True,
        'chart_data': {
            'labels': labels,
            'datasets': [{
                'label': 'Visits',
                'data': data,
                'backgroundColor': '#4BC0C0'
            }]
        }
    }), 200


@doctor_bp.route('/charts/monthly-summary', methods=['GET'])
@doctor_required
def get_monthly_summary_chart():
    """Get monthly appointment summary for bar chart."""
    from sqlalchemy import func, extract

    doctor = get_current_doctor()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404

    months = request.args.get('months', 6, type=int)
    end_date = date.today()
    start_date = end_date - timedelta(days=months * 30)

    results = db.session.query(
        extract('year', Appointment.appointment_date).label('year'),
        extract('month', Appointment.appointment_date).label('month'),
        func.count(Appointment.id)
    ).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= start_date
    ).group_by(
        extract('year', Appointment.appointment_date),
        extract('month', Appointment.appointment_date)
    ).order_by(
        extract('year', Appointment.appointment_date),
        extract('month', Appointment.appointment_date)
    ).all()

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    labels = [f"{month_names[int(r[1])-1]} {int(r[0])}" for r in results]
    data = [r[2] for r in results]

    return jsonify({
        'success': True,
        'chart_data': {
            'labels': labels,
            'datasets': [{
                'label': 'Appointments',
                'data': data,
                'backgroundColor': '#36A2EB'
            }]
        }
    }), 200
