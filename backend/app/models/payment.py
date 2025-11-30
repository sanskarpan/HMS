from datetime import datetime
from . import db, TimestampMixin


class Payment(db.Model, TimestampMixin):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='card')
    card_last_four = db.Column(db.String(4), nullable=True)

    status = db.Column(db.String(20), default='pending')
    transaction_id = db.Column(db.String(100), nullable=True)

    paid_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    VALID_STATUSES = ['pending', 'completed', 'failed', 'refunded']
    VALID_METHODS = ['card', 'cash', 'insurance']

    appointment = db.relationship('Appointment', backref=db.backref('payment', uselist=False))
    patient = db.relationship('Patient', backref=db.backref('payments', lazy='dynamic'))

    def __init__(self, appointment_id, patient_id, amount, **kwargs):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.amount = amount
        self.payment_method = kwargs.get('payment_method', 'card')
        self.card_last_four = kwargs.get('card_last_four')
        self.status = kwargs.get('status', 'pending')
        self.notes = kwargs.get('notes')

    def mark_completed(self, transaction_id=None):
        self.status = 'completed'
        self.paid_at = datetime.utcnow()
        if transaction_id:
            self.transaction_id = transaction_id

    def mark_failed(self, reason=None):
        self.status = 'failed'
        if reason:
            self.notes = reason

    def to_dict(self, include_appointment=False):
        data = {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'card_last_four': self.card_last_four,
            'status': self.status,
            'transaction_id': self.transaction_id,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_appointment and self.appointment:
            data['appointment'] = {
                'id': self.appointment.id,
                'date': self.appointment.appointment_date.isoformat(),
                'time': self.appointment.appointment_time.strftime('%H:%M'),
                'doctor_name': self.appointment.doctor.full_name if self.appointment.doctor else None
            }

        return data

    def __repr__(self):
        return f'<Payment {self.id} Apt:{self.appointment_id} ${self.amount} {self.status}>'

    @classmethod
    def get_by_appointment(cls, appointment_id):
        return cls.query.filter_by(appointment_id=appointment_id).first()

    @classmethod
    def get_patient_payments(cls, patient_id):
        return cls.query.filter_by(patient_id=patient_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_pending_payments(cls, patient_id):
        return cls.query.filter_by(patient_id=patient_id, status='pending').all()
