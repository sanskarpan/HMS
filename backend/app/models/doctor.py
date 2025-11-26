"""
Doctor model for the Hospital Management System.
Represents medical professionals with their profiles and department associations.
"""
from . import db, TimestampMixin


class Doctor(db.Model, TimestampMixin):
    """
    Doctor model for medical professionals.

    Attributes:
        user_id: Link to the User model for authentication
        full_name: Doctor's full name
        department_id: Associated department/specialization
        qualification: Medical qualifications (MBBS, MD, etc.)
        experience_years: Years of experience
        phone: Contact number
        bio: Profile description
        consultation_fee: Fee per consultation
    """
    __tablename__ = 'doctors'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)

    # Profile information
    full_name = db.Column(db.String(150), nullable=False, index=True)
    qualification = db.Column(db.String(200), nullable=True)  # e.g., "MBBS, MD - Cardiology"
    experience_years = db.Column(db.Integer, default=0)
    phone = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    consultation_fee = db.Column(db.Float, default=0.0)

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='doctor_profile')
    department = db.relationship('Department', back_populates='doctors')
    availability = db.relationship('DoctorAvailability', back_populates='doctor',
                                   lazy='dynamic', cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', back_populates='doctor',
                                   lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, user_id, department_id, full_name, **kwargs):
        """Initialize a new doctor profile."""
        self.user_id = user_id
        self.department_id = department_id
        self.full_name = full_name
        self.qualification = kwargs.get('qualification')
        self.experience_years = kwargs.get('experience_years', 0)
        self.phone = kwargs.get('phone')
        self.bio = kwargs.get('bio')
        self.consultation_fee = kwargs.get('consultation_fee', 0.0)

    @property
    def email(self):
        """Get email from associated user."""
        return self.user.email if self.user else None

    @property
    def is_blacklisted(self):
        """Check if doctor's user account is blacklisted."""
        return self.user.is_blacklisted if self.user else False

    @property
    def upcoming_appointments(self):
        """Get upcoming appointments."""
        from datetime import date
        return self.appointments.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.status == 'booked'
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()

    @property
    def today_appointments_count(self):
        """Get count of today's appointments."""
        from datetime import date
        return self.appointments.filter(
            Appointment.appointment_date == date.today()
        ).count()

    def get_appointments_for_date(self, date):
        """Get all appointments for a specific date."""
        from .appointment import Appointment
        return self.appointments.filter(
            Appointment.appointment_date == date
        ).order_by(Appointment.appointment_time).all()

    def get_availability_for_date(self, date):
        """Get availability for a specific date."""
        return self.availability.filter_by(date=date).first()

    def to_dict(self, include_user=False, include_department=True):
        """Convert doctor to dictionary representation."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'qualification': self.qualification,
            'experience_years': self.experience_years,
            'phone': self.phone,
            'bio': self.bio,
            'consultation_fee': self.consultation_fee,
            'is_active': self.is_active,
            'email': self.email,
            'is_blacklisted': self.is_blacklisted,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_department and self.department:
            data['department'] = {
                'id': self.department.id,
                'name': self.department.name
            }

        if include_user and self.user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email
            }

        return data

    def __repr__(self):
        return f'<Doctor {self.full_name}>'

    @classmethod
    def find_by_user_id(cls, user_id):
        """Find doctor by user ID."""
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def get_all_active(cls):
        """Get all active doctors."""
        return cls.query.filter_by(is_active=True).all()

    @classmethod
    def search(cls, query=None, department_id=None):
        """Search doctors by name or filter by department."""
        base_query = cls.query.filter_by(is_active=True)

        if department_id:
            base_query = base_query.filter_by(department_id=department_id)

        if query:
            search_term = f'%{query}%'
            base_query = base_query.filter(
                (cls.full_name.ilike(search_term)) |
                (cls.qualification.ilike(search_term))
            )

        return base_query.order_by(cls.full_name).all()

    @classmethod
    def get_by_department(cls, department_id):
        """Get all active doctors in a department."""
        return cls.query.filter_by(
            department_id=department_id,
            is_active=True
        ).order_by(cls.full_name).all()


# Importing Appointment here to avoid circular imports
from .appointment import Appointment
