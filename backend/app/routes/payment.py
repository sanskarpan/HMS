"""
Payment routes - payment processing, history, and management
"""
import uuid
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from backend.app.models import db, Payment, Appointment, Patient
from backend.app.utils.decorators import patient_required, admin_required
from backend.app.utils import get_current_user_from_request

payment_bp = Blueprint('payment', __name__)


def get_current_patient():
    """Return patient profile for logged-in user."""
    user = get_current_user_from_request()
    if user and user.patient_profile:
        return user.patient_profile
    return None


def generate_transaction_id():
    """Generate a unique transaction identifier."""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    unique_part = uuid.uuid4().hex[:8].upper()
    return f"TXN-{timestamp}-{unique_part}"


def simulate_card_payment(card_number, amount):
    """
    Simulate card payment processing.
    In production, this would integrate with a real payment gateway.
    Returns (success, transaction_id, message)
    """
    if not card_number or len(card_number) < 4:
        return False, None, "Invalid card number"

    last_four = card_number[-4:]

    if card_number.startswith('4000000000000002'):
        return False, None, "Card declined"

    if card_number.startswith('4000000000000069'):
        return False, None, "Expired card"

    transaction_id = generate_transaction_id()
    return True, transaction_id, "Payment successful"


@payment_bp.route('/initiate', methods=['POST'])
@patient_required
def initiate_payment():
    """Start a payment for an appointment."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    data = request.get_json()
    appointment_id = data.get('appointment_id')

    if not appointment_id:
        return jsonify({'success': False, 'message': 'Appointment ID required'}), 400

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        patient_id=patient.id
    ).first()

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

    if appointment.status not in ['booked', 'completed']:
        return jsonify({
            'success': False,
            'message': f'Cannot pay for {appointment.status} appointment'
        }), 400

    existing_payment = Payment.get_by_appointment(appointment_id)
    if existing_payment and existing_payment.status == 'completed':
        return jsonify({
            'success': False,
            'message': 'Payment already completed for this appointment'
        }), 409

    amount = appointment.doctor.consultation_fee if appointment.doctor else 0
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Invalid consultation fee'}), 400

    try:
        if existing_payment and existing_payment.status in ['pending', 'failed']:
            existing_payment.amount = amount
            existing_payment.status = 'pending'
            payment = existing_payment
        else:
            payment = Payment(
                appointment_id=appointment_id,
                patient_id=patient.id,
                amount=amount
            )
            db.session.add(payment)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Payment initiated',
            'payment': payment.to_dict(include_appointment=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to initiate payment: {str(e)}'}), 500


@payment_bp.route('/process', methods=['POST'])
@patient_required
def process_payment():
    """Process payment with card details."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    data = request.get_json()
    payment_id = data.get('payment_id')
    card_number = data.get('card_number', '').replace(' ', '').replace('-', '')
    payment_method = data.get('payment_method', 'card')

    if not payment_id:
        return jsonify({'success': False, 'message': 'Payment ID required'}), 400

    payment = Payment.query.filter_by(
        id=payment_id,
        patient_id=patient.id
    ).first()

    if not payment:
        return jsonify({'success': False, 'message': 'Payment not found'}), 404

    if payment.status == 'completed':
        return jsonify({'success': False, 'message': 'Payment already completed'}), 409

    if payment_method == 'card':
        if not card_number or len(card_number) < 13:
            return jsonify({'success': False, 'message': 'Valid card number required'}), 400

        success, transaction_id, message = simulate_card_payment(card_number, payment.amount)

        if success:
            payment.payment_method = 'card'
            payment.card_last_four = card_number[-4:]
            payment.mark_completed(transaction_id)
        else:
            payment.mark_failed(message)

    elif payment_method == 'cash':
        payment.payment_method = 'cash'
        payment.mark_completed(generate_transaction_id())

    elif payment_method == 'insurance':
        payment.payment_method = 'insurance'
        payment.notes = data.get('insurance_id', 'Insurance claim submitted')
        payment.mark_completed(generate_transaction_id())

    else:
        return jsonify({'success': False, 'message': 'Invalid payment method'}), 400

    try:
        db.session.commit()

        if payment.status == 'completed':
            return jsonify({
                'success': True,
                'message': 'Payment successful',
                'payment': payment.to_dict(include_appointment=True)
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'Payment failed: {payment.notes}',
                'payment': payment.to_dict()
            }), 402

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Payment processing error: {str(e)}'}), 500


@payment_bp.route('/history', methods=['GET'])
@patient_required
def get_payment_history():
    """Get patient's payment history."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    status = request.args.get('status')

    payments = Payment.get_patient_payments(patient.id)

    if status:
        payments = [p for p in payments if p.status == status]

    return jsonify({
        'success': True,
        'payments': [p.to_dict(include_appointment=True) for p in payments],
        'total': len(payments)
    }), 200


@payment_bp.route('/pending', methods=['GET'])
@patient_required
def get_pending_payments():
    """Get patient's pending payments."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    pending = Payment.get_pending_payments(patient.id)

    return jsonify({
        'success': True,
        'payments': [p.to_dict(include_appointment=True) for p in pending],
        'total': len(pending)
    }), 200


@payment_bp.route('/<int:payment_id>', methods=['GET'])
@patient_required
def get_payment_details(payment_id):
    """Get specific payment details."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    payment = Payment.query.filter_by(
        id=payment_id,
        patient_id=patient.id
    ).first()

    if not payment:
        return jsonify({'success': False, 'message': 'Payment not found'}), 404

    return jsonify({
        'success': True,
        'payment': payment.to_dict(include_appointment=True)
    }), 200


@payment_bp.route('/appointment/<int:appointment_id>', methods=['GET'])
@patient_required
def get_appointment_payment(appointment_id):
    """Get payment status for an appointment."""
    patient = get_current_patient()
    if not patient:
        return jsonify({'success': False, 'message': 'Patient profile not found'}), 404

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        patient_id=patient.id
    ).first()

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

    payment = Payment.get_by_appointment(appointment_id)

    if payment:
        return jsonify({
            'success': True,
            'has_payment': True,
            'payment': payment.to_dict(include_appointment=True)
        }), 200
    else:
        return jsonify({
            'success': True,
            'has_payment': False,
            'amount_due': appointment.doctor.consultation_fee if appointment.doctor else 0
        }), 200


@payment_bp.route('/admin/all', methods=['GET'])
@admin_required
def admin_get_all_payments():
    """Admin: Get all payments with filters."""
    status = request.args.get('status')
    patient_id = request.args.get('patient_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    query = Payment.query

    if status:
        query = query.filter_by(status=status)

    if patient_id:
        query = query.filter_by(patient_id=patient_id)

    if date_from:
        from_date = datetime.strptime(date_from, '%Y-%m-%d')
        query = query.filter(Payment.created_at >= from_date)

    if date_to:
        to_date = datetime.strptime(date_to, '%Y-%m-%d')
        query = query.filter(Payment.created_at <= to_date)

    payments = query.order_by(Payment.created_at.desc()).all()

    total_amount = sum(p.amount for p in payments if p.status == 'completed')

    return jsonify({
        'success': True,
        'payments': [p.to_dict(include_appointment=True) for p in payments],
        'total': len(payments),
        'total_revenue': total_amount
    }), 200


@payment_bp.route('/admin/<int:payment_id>/refund', methods=['POST'])
@admin_required
def admin_refund_payment(payment_id):
    """Admin: Process refund for a payment."""
    payment = Payment.query.get(payment_id)

    if not payment:
        return jsonify({'success': False, 'message': 'Payment not found'}), 404

    if payment.status != 'completed':
        return jsonify({
            'success': False,
            'message': f'Cannot refund {payment.status} payment'
        }), 400

    data = request.get_json() or {}
    reason = data.get('reason', 'Admin initiated refund')

    try:
        payment.status = 'refunded'
        payment.notes = f"Refunded: {reason}"
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Payment refunded',
            'payment': payment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Refund failed: {str(e)}'}), 500


@payment_bp.route('/admin/stats', methods=['GET'])
@admin_required
def admin_payment_stats():
    """Admin: Get payment statistics."""
    from sqlalchemy import func
    from datetime import timedelta

    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    total_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'completed'
    ).scalar() or 0

    weekly_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'completed',
        Payment.paid_at >= week_ago
    ).scalar() or 0

    monthly_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'completed',
        Payment.paid_at >= month_ago
    ).scalar() or 0

    total_payments = Payment.query.count()
    completed_payments = Payment.query.filter_by(status='completed').count()
    pending_payments = Payment.query.filter_by(status='pending').count()
    failed_payments = Payment.query.filter_by(status='failed').count()
    refunded_payments = Payment.query.filter_by(status='refunded').count()

    method_stats = db.session.query(
        Payment.payment_method,
        func.count(Payment.id),
        func.sum(Payment.amount)
    ).filter(
        Payment.status == 'completed'
    ).group_by(Payment.payment_method).all()

    payment_methods = {
        method: {'count': count, 'amount': amount or 0}
        for method, count, amount in method_stats
    }

    return jsonify({
        'success': True,
        'stats': {
            'total_revenue': total_revenue,
            'weekly_revenue': weekly_revenue,
            'monthly_revenue': monthly_revenue,
            'total_payments': total_payments,
            'by_status': {
                'completed': completed_payments,
                'pending': pending_payments,
                'failed': failed_payments,
                'refunded': refunded_payments
            },
            'by_method': payment_methods
        }
    }), 200
