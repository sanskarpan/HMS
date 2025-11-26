"""
Admin API Routes for the Hospital Management System.
Handles admin dashboard, doctor management, patient management, and appointment oversight.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date

from backend.app.models import db, User, Doctor, Patient, Appointment, Department
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

