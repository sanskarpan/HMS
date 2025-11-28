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

