from datetime import datetime
from . import db


class AppointmentStatusLog(db.Model):
    __tablename__ = 'appointment_status_logs'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=False)
    changed_by_role = db.Column(db.String(20), nullable=False)
    changed_by_id = db.Column(db.Integer, nullable=True)

    # When and why
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reason = db.Column(db.Text, nullable=True)

    # Relationship
    appointment = db.relationship('Appointment', backref=db.backref('status_logs', lazy='dynamic'))

    def __init__(self, appointment_id, new_status, changed_by_role, **kwargs):
        self.appointment_id = appointment_id
        self.new_status = new_status
        self.changed_by_role = changed_by_role
        self.old_status = kwargs.get('old_status')
        self.changed_by_id = kwargs.get('changed_by_id')
        self.reason = kwargs.get('reason')

    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'changed_by_role': self.changed_by_role,
            'changed_by_id': self.changed_by_id,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
            'reason': self.reason
        }

    def __repr__(self):
        return f'<StatusLog {self.id} Apt:{self.appointment_id} {self.old_status}->{self.new_status}>'

    @classmethod
    def log_status_change(cls, appointment, new_status, changed_by_role, changed_by_id=None, reason=None):
        """Helper method to log a status change."""
        log = cls(
            appointment_id=appointment.id,
            old_status=appointment.status,
            new_status=new_status,
            changed_by_role=changed_by_role,
            changed_by_id=changed_by_id,
            reason=reason
        )
        db.session.add(log)
        return log

    @classmethod
    def get_appointment_history(cls, appointment_id):
        """Get all status changes for an appointment."""
        return cls.query.filter_by(appointment_id=appointment_id).order_by(cls.changed_at).all()
