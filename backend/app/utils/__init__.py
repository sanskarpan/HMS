"""
Utility functions and decorators for the Hospital Management System.
"""
from .auth import (
    get_current_user,
    get_current_user_id,
    generate_tokens,
    create_auth_response,
    validate_login_credentials
)
from .decorators import (
    login_required,
    admin_required,
    doctor_required,
    patient_required,
    roles_required,
    admin_or_doctor_required,
    get_current_user_from_request
)

__all__ = [
    # Auth utilities
    'get_current_user',
    'get_current_user_id',
    'generate_tokens',
    'create_auth_response',
    'validate_login_credentials',
    # Decorators
    'login_required',
    'admin_required',
    'doctor_required',
    'patient_required',
    'roles_required',
    'admin_or_doctor_required',
    'get_current_user_from_request'
]
