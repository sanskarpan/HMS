from datetime import date
from . import db, TimestampMixin


class Patient(db.Model, TimestampMixin):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False, index=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(20), nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)
    medical_history = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    VALID_GENDERS = ['male', 'female', 'other']
    VALID_BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

    user = db.relationship('User', back_populates='patient_profile')
    appointments = db.relationship('Appointment', back_populates='patient',
                                   lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, user_id, full_name, phone, **kwargs):
        self.user_id = user_id
        self.full_name = full_name
        self.phone = phone
        self.date_of_birth = kwargs.get('date_of_birth')
        self.gender = kwargs.get('gender')
        self.address = kwargs.get('address')
        self.emergency_contact = kwargs.get('emergency_contact')
        self.blood_group = kwargs.get('blood_group')
        self.medical_history = kwargs.get('medical_history')

    @property
    def email(self):
        return self.user.email if self.user else None

    @property
    def username(self):
        return self.user.username if self.user else None

    @property
    def is_blacklisted(self):
        return self.user.is_blacklisted if self.user else False

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        age = today.year - self.date_of_birth.year
        # Adjust if birthday hasn't occurred this year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age

    @property
    def upcoming_appointments(self):
        from .appointment import Appointment
        return self.appointments.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.status == 'booked'
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()

    @property
    def past_appointments(self):
        from .appointment import Appointment
        return self.appointments.filter(
            (Appointment.appointment_date < date.today()) |
            (Appointment.status.in_(['completed', 'cancelled']))
        ).order_by(Appointment.appointment_date.desc()).all()

    def get_treatment_history(self):
        from .appointment import Appointment
        from .treatment import Treatment

        completed_appointments = self.appointments.filter(
            Appointment.status == 'completed'
        ).all()

        treatments = []
        for apt in completed_appointments:
            if apt.treatment:
                treatments.append({
                    'appointment': apt.to_dict(),
                    'treatment': apt.treatment.to_dict()
                })

        return treatments

    def to_dict(self, include_user=False, include_appointments=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'blood_group': self.blood_group,
            'medical_history': self.medical_history,
            'is_active': self.is_active,
            'email': self.email,
            'is_blacklisted': self.is_blacklisted,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_user and self.user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email
            }

        if include_appointments:
            data['upcoming_appointments'] = [apt.to_dict() for apt in self.upcoming_appointments]

        return data

    def __repr__(self):
        return f'<Patient {self.full_name}>'

    @classmethod
    def find_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def get_all_active(cls):
        return cls.query.filter_by(is_active=True).all()

    @classmethod
    def search(cls, query):
        from .user import User

        search_term = f'%{query}%'
        return cls.query.join(User).filter(
            cls.is_active == True,
            (cls.full_name.ilike(search_term)) |
            (cls.phone.ilike(search_term)) |
            (User.email.ilike(search_term))
        ).order_by(cls.full_name).all()
