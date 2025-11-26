"""
Appointment model for the Hospital Management System.
Handles scheduling of doctor-patient meetings with conflict prevention.
"""
from datetime import datetime, date, timedelta
from . import db, TimestampMixin


class Appointment(db.Model, TimestampMixin):
    """
    Appointment model for doctor-patient meetings.

    Attributes:
        patient_id: Patient booking the appointment
        doctor_id: Doctor for the appointment
        department_id: Department/specialization
        appointment_date: Date of appointment
        appointment_time: Start time of appointment
        status: Current status (booked, completed, cancelled, no_show)
        reason: Reason for visit
        notes: Additional notes
    """
    __tablename__ = 'appointments'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    # Appointment timing
    appointment_date = db.Column(db.Date, nullable=False, index=True)
    appointment_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, default=30)  # Duration in minutes

    # Status and details
    status = db.Column(db.String(20), default='booked', nullable=False, index=True)
    reason = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Cancellation tracking
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancelled_by = db.Column(db.String(20), nullable=True)  # patient, doctor, admin
    cancellation_reason = db.Column(db.Text, nullable=True)

    # Rescheduling tracking
    original_date = db.Column(db.Date, nullable=True)
    original_time = db.Column(db.Time, nullable=True)
    rescheduled_at = db.Column(db.DateTime, nullable=True)

    # Valid statuses
    VALID_STATUSES = ['booked', 'completed', 'cancelled', 'no_show']

    # Unique constraint: prevent double booking
    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'appointment_date', 'appointment_time',
                            name='unique_doctor_appointment_slot'),
    )

    # Relationships
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')
    department = db.relationship('Department', back_populates='appointments')
    treatment = db.relationship('Treatment', back_populates='appointment',
                                uselist=False, cascade='all, delete-orphan')

    def __init__(self, patient_id, doctor_id, appointment_date, appointment_time, **kwargs):
        """Initialize a new appointment."""
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.department_id = kwargs.get('department_id')
        self.duration = kwargs.get('duration', 30)
        self.reason = kwargs.get('reason')
        self.notes = kwargs.get('notes')
        self.status = 'booked'

    @property
    def end_time(self):
        """Calculate end time based on start time and duration."""
        if self.appointment_time:
            start_datetime = datetime.combine(date.today(), self.appointment_time)
            end_datetime = start_datetime + timedelta(minutes=self.duration)
            return end_datetime.time()
        return None

    @property
    def is_past(self):
        """Check if appointment date has passed."""
        return self.appointment_date < date.today()

    @property
    def is_today(self):
        """Check if appointment is today."""
        return self.appointment_date == date.today()

    @property
    def is_upcoming(self):
        """Check if appointment is in the future."""
        return self.appointment_date > date.today()

    @property
    def can_cancel(self):
        """Check if appointment can be cancelled."""
        return self.status == 'booked' and not self.is_past

    @property
    def can_reschedule(self):
        """Check if appointment can be rescheduled."""
        return self.status == 'booked' and not self.is_past

    def complete(self):
        """Mark appointment as completed."""
        if self.status != 'booked':
            raise ValueError(f"Cannot complete appointment with status: {self.status}")
        self.status = 'completed'

    def cancel(self, cancelled_by, reason=None):
        """
        Cancel the appointment.

        Args:
            cancelled_by: Who cancelled (patient, doctor, admin)
            reason: Optional cancellation reason
        """
        if self.status != 'booked':
            raise ValueError(f"Cannot cancel appointment with status: {self.status}")

        self.status = 'cancelled'
        self.cancelled_at = datetime.utcnow()
        self.cancelled_by = cancelled_by
        self.cancellation_reason = reason

    def mark_no_show(self):
        """Mark appointment as no-show."""
        if self.status != 'booked':
            raise ValueError(f"Cannot mark no-show for appointment with status: {self.status}")
        self.status = 'no_show'

    def reschedule(self, new_date, new_time):
        """
        Reschedule appointment to new date/time.

        Args:
            new_date: New appointment date
            new_time: New appointment time
        """
        if not self.can_reschedule:
            raise ValueError("Cannot reschedule this appointment")

        # Store original schedule if not already stored
        if not self.original_date:
            self.original_date = self.appointment_date
            self.original_time = self.appointment_time

        self.appointment_date = new_date
        self.appointment_time = new_time
        self.rescheduled_at = datetime.utcnow()

    def to_dict(self, include_patient=False, include_doctor=False, include_treatment=False):
        """Convert appointment to dictionary representation."""
        data = {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'department_id': self.department_id,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.strftime('%H:%M') if self.appointment_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'duration': self.duration,
            'status': self.status,
            'reason': self.reason,
            'notes': self.notes,
            'is_past': self.is_past,
            'is_today': self.is_today,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancelled_by': self.cancelled_by,
            'cancellation_reason': self.cancellation_reason,
            'original_date': self.original_date.isoformat() if self.original_date else None,
            'original_time': self.original_time.strftime('%H:%M') if self.original_time else None,
            'rescheduled_at': self.rescheduled_at.isoformat() if self.rescheduled_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_patient and self.patient:
            data['patient'] = {
                'id': self.patient.id,
                'full_name': self.patient.full_name,
                'phone': self.patient.phone
            }

        if include_doctor and self.doctor:
            data['doctor'] = {
                'id': self.doctor.id,
                'full_name': self.doctor.full_name,
                'department': self.doctor.department.name if self.doctor.department else None
            }

        if self.department:
            data['department_name'] = self.department.name

        if include_treatment and self.treatment:
            data['treatment'] = self.treatment.to_dict()

        return data

    def __repr__(self):
        return f'<Appointment {self.id} Patient:{self.patient_id} Doctor:{self.doctor_id} {self.appointment_date}>'

    @classmethod
    def check_slot_available(cls, doctor_id, appointment_date, appointment_time):
        """
        Check if a time slot is available for a doctor.

        Returns:
            True if slot is available, False otherwise
        """
        existing = cls.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='booked'
        ).first()
        return existing is None

    @classmethod
    def get_booked_slots(cls, doctor_id, appointment_date):
        """Get all booked time slots for a doctor on a date."""
        appointments = cls.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            status='booked'
        ).all()
        return [apt.appointment_time for apt in appointments]

    @classmethod
    def get_by_doctor_and_date(cls, doctor_id, appointment_date):
        """Get all appointments for a doctor on a specific date."""
        return cls.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date
        ).order_by(cls.appointment_time).all()

    @classmethod
    def get_today_appointments(cls, doctor_id=None, patient_id=None):
        """Get today's appointments for a doctor or patient."""
        query = cls.query.filter_by(appointment_date=date.today())

        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        if patient_id:
            query = query.filter_by(patient_id=patient_id)

        return query.order_by(cls.appointment_time).all()

    @classmethod
    def get_upcoming(cls, doctor_id=None, patient_id=None, days=7):
        """Get upcoming appointments for next N days."""
        end_date = date.today() + timedelta(days=days)

        query = cls.query.filter(
            cls.appointment_date >= date.today(),
            cls.appointment_date <= end_date,
            cls.status == 'booked'
        )

        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        if patient_id:
            query = query.filter_by(patient_id=patient_id)

        return query.order_by(cls.appointment_date, cls.appointment_time).all()
