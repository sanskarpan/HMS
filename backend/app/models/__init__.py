"""
Database models for the Hospital Management System.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()


class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps to models."""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Import all models to register them with SQLAlchemy
from .user import User
from .department import Department
from .doctor import Doctor
from .availability import DoctorAvailability
from .patient import Patient
from .appointment import Appointment
from .treatment import Treatment
from .status_log import AppointmentStatusLog
from .payment import Payment

# Export all models
__all__ = [
    'db',
    'TimestampMixin',
    'User',
    'Department',
    'Doctor',
    'DoctorAvailability',
    'Patient',
    'Appointment',
    'Treatment',
    'AppointmentStatusLog',
    'Payment'
]
