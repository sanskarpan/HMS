from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, TimestampMixin


class User(db.Model, TimestampMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    doctor_profile = db.relationship('Doctor', back_populates='user', uselist=False, cascade='all, delete-orphan')
    patient_profile = db.relationship('Patient', back_populates='user', uselist=False, cascade='all, delete-orphan')

    VALID_ROLES = ['admin', 'doctor', 'patient']

    def __init__(self, username, email, password, role='patient'):
        self.username = username
        self.email = email.lower()
        self.set_password(password)
        self.set_role(role)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_role(self, role):
        if role not in self.VALID_ROLES:
            raise ValueError(f"Invalid role: {role}. Must be one of {self.VALID_ROLES}")
        self.role = role

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_doctor(self):
        return self.role == 'doctor'

    @property
    def is_patient(self):
        return self.role == 'patient'

    @property
    def can_login(self):
        return self.is_active and not self.is_blacklisted

    def to_dict(self, include_profile=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'is_blacklisted': self.is_blacklisted,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_profile:
            if self.is_doctor and self.doctor_profile:
                data['profile'] = self.doctor_profile.to_dict()
            elif self.is_patient and self.patient_profile:
                data['profile'] = self.patient_profile.to_dict()

        return data

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email.lower()).first()

    @classmethod
    def find_by_username_or_email(cls, identifier):
        return cls.query.filter(
            (cls.username == identifier) | (cls.email == identifier.lower())
        ).first()
