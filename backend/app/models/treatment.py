from . import db, TimestampMixin


class Treatment(db.Model, TimestampMixin):
    __tablename__ = 'treatments'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'),
                               unique=True, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    tests_recommended = db.Column(db.Text, nullable=True)

    # Follow-up
    follow_up_date = db.Column(db.Date, nullable=True)
    follow_up_notes = db.Column(db.Text, nullable=True)

    # Visit type
    visit_type = db.Column(db.String(30), default='in-person')

    # Valid visit types
    VALID_VISIT_TYPES = ['in-person', 'follow-up', 'emergency', 'routine-checkup']

    # Relationships
    appointment = db.relationship('Appointment', back_populates='treatment')

    def __init__(self, appointment_id, diagnosis, **kwargs):
        """Initialize a new treatment record."""
        self.appointment_id = appointment_id
        self.diagnosis = diagnosis
        self.prescription = kwargs.get('prescription')
        self.notes = kwargs.get('notes')
        self.tests_recommended = kwargs.get('tests_recommended')
        self.follow_up_date = kwargs.get('follow_up_date')
        self.follow_up_notes = kwargs.get('follow_up_notes')
        self.visit_type = kwargs.get('visit_type', 'in-person')

    @property
    def patient(self):
        """Get patient from linked appointment."""
        return self.appointment.patient if self.appointment else None

    @property
    def doctor(self):
        """Get doctor from linked appointment."""
        return self.appointment.doctor if self.appointment else None

    @property
    def appointment_date(self):
        """Get appointment date."""
        return self.appointment.appointment_date if self.appointment else None

    def get_prescription_list(self):
        """Parse prescription text into a list of medications."""
        if not self.prescription:
            return []
        # Assuming prescriptions are stored as newline-separated entries
        return [med.strip() for med in self.prescription.split('\n') if med.strip()]

    def get_tests_list(self):
        """Parse tests_recommended into a list."""
        if not self.tests_recommended:
            return []
        return [test.strip() for test in self.tests_recommended.split('\n') if test.strip()]

    def to_dict(self, include_appointment=False):
        """Convert treatment to dictionary representation."""
        data = {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'prescription_list': self.get_prescription_list(),
            'notes': self.notes,
            'tests_recommended': self.tests_recommended,
            'tests_list': self.get_tests_list(),
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'follow_up_notes': self.follow_up_notes,
            'visit_type': self.visit_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_appointment and self.appointment:
            data['appointment'] = {
                'id': self.appointment.id,
                'date': self.appointment.appointment_date.isoformat(),
                'time': self.appointment.appointment_time.strftime('%H:%M'),
                'doctor_id': self.appointment.doctor_id,
                'doctor_name': self.doctor.full_name if self.doctor else None,
                'patient_id': self.appointment.patient_id,
                'patient_name': self.patient.full_name if self.patient else None
            }

        return data

    def to_export_dict(self):
        """Convert treatment to export format for CSV."""
        return {
            'treatment_id': self.id,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else '',
            'consulting_doctor': self.doctor.full_name if self.doctor else '',
            'department': self.doctor.department.name if self.doctor and self.doctor.department else '',
            'visit_type': self.visit_type,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription or '',
            'tests_recommended': self.tests_recommended or '',
            'notes': self.notes or '',
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else ''
        }

    def __repr__(self):
        return f'<Treatment {self.id} Appointment:{self.appointment_id}>'

    @classmethod
    def find_by_appointment(cls, appointment_id):
        """Find treatment by appointment ID."""
        return cls.query.filter_by(appointment_id=appointment_id).first()

    @classmethod
    def get_patient_history(cls, patient_id):
        """Get all treatments for a patient."""
        from .appointment import Appointment

        return cls.query.join(Appointment).filter(
            Appointment.patient_id == patient_id
        ).order_by(Appointment.appointment_date.desc()).all()

    @classmethod
    def get_doctor_treatments(cls, doctor_id, month=None, year=None):
        """Get treatments by a doctor, optionally filtered by month/year."""
        from .appointment import Appointment
        from datetime import date

        query = cls.query.join(Appointment).filter(
            Appointment.doctor_id == doctor_id
        )

        if month and year:
            # Filter by specific month
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)

            query = query.filter(
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date < end_date
            )

        return query.order_by(Appointment.appointment_date.desc()).all()
