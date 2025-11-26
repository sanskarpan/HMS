"""
Authentication utilities for JWT token handling.
"""
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt
)

from backend.app.models import User


def generate_tokens(user):
    """
    Generate access and refresh tokens for a user.

    Args:
        user: User model instance

    Returns:
        dict with access_token and refresh_token
    """
    # Identity must be a string or int (not dict)
    identity = str(user.id)

    # Store additional user info in claims
    additional_claims = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }

    access_token = create_access_token(
        identity=identity,
        additional_claims=additional_claims
    )

    refresh_token = create_refresh_token(
        identity=identity,
        additional_claims=additional_claims
    )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def get_current_user():
    """
    Get the current authenticated user from JWT token.

    Returns:
        User model instance or None
    """
    try:
        # Identity is the user_id as string
        identity = get_jwt_identity()
        if identity:
            return User.query.get(int(identity))
        return None
    except Exception:
        return None


def get_current_user_id():
    """
    Get the current user's ID from JWT token.

    Returns:
        int user_id or None
    """
    try:
        identity = get_jwt_identity()
        if identity:
            return int(identity)
        return None
    except Exception:
        return None


def get_current_user_role():
    """
    Get the current user's role from JWT claims.

    Returns:
        str role or None
    """
    try:
        claims = get_jwt()
        return claims.get('role')
    except Exception:
        return None


def create_auth_response(user, message="Login successful"):
    """
    Create a standardized authentication response.

    Args:
        user: User model instance
        message: Success message

    Returns:
        dict with tokens and user info
    """
    tokens = generate_tokens(user)

    # Update last login
    user.update_last_login()

    # Get profile data based on role
    profile = None
    if user.is_doctor and user.doctor_profile:
        profile = user.doctor_profile.to_dict()
    elif user.is_patient and user.patient_profile:
        profile = user.patient_profile.to_dict()

    return {
        'success': True,
        'message': message,
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'profile': profile
        }
    }


def validate_login_credentials(identifier, password):
    """
    Validate user login credentials.

    Args:
        identifier: Username or email
        password: Plain text password

    Returns:
        tuple (User or None, error_message or None)
    """
    # Find user by username or email
    user = User.find_by_username_or_email(identifier)

    if not user:
        return None, "Invalid username or email"

    if not user.check_password(password):
        return None, "Invalid password"

    if not user.is_active:
        return None, "Account is deactivated"

    if user.is_blacklisted:
        return None, "Account has been blacklisted. Please contact admin."

    return user, None
