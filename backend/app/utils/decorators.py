"""
Role-Based Access Control (RBAC) decorators for route protection.
DRY implementation with a base verification function.
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

from backend.app.models import User


def _verify_user_access(required_roles=None):
    """
    Base function for verifying user authentication and authorization.

    Args:
        required_roles: List of allowed roles, or None for any authenticated user

    Returns:
        tuple (user, error_response, status_code)
        If successful: (user, None, None)
        If error: (None, error_dict, status_code)
    """
    try:
        verify_jwt_in_request()

        # Identity is user_id as string
        identity = get_jwt_identity()

        if not identity:
            return None, {
                'success': False,
                'message': 'Invalid token',
                'error': 'invalid_token'
            }, 401

        # Get user from database
        user = User.query.get(int(identity))

        if not user:
            return None, {
                'success': False,
                'message': 'User not found',
                'error': 'user_not_found'
            }, 401

        if not user.can_login:
            return None, {
                'success': False,
                'message': 'Account is deactivated or blacklisted',
                'error': 'account_inactive'
            }, 403

        # Check role if required
        if required_roles and user.role not in required_roles:
            role_names = ', '.join(required_roles)
            return None, {
                'success': False,
                'message': f'Access denied. Required role(s): {role_names}',
                'error': 'forbidden'
            }, 403

        return user, None, None

    except Exception as e:
        return None, {
            'success': False,
            'message': 'Authentication required',
            'error': 'auth_required'
        }, 401


def _create_role_decorator(required_roles=None):
    """
    Factory function to create role-based decorators.

    Args:
        required_roles: List of allowed roles, or None for any authenticated user

    Returns:
        Decorator function
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user, error, status_code = _verify_user_access(required_roles)

            if error:
                return jsonify(error), status_code

            return fn(*args, **kwargs)
        return wrapper
    return decorator


# Public decorators
def login_required(fn):
    """
    Decorator to require authentication for a route.
    Returns 401 if not authenticated.
    """
    return _create_role_decorator(required_roles=None)(fn)


def roles_required(allowed_roles):
    """
    Decorator to require specific roles for a route.

    Args:
        allowed_roles: List of allowed role strings (e.g., ['admin', 'doctor'])

    Usage:
        @roles_required(['admin', 'doctor'])
        def my_route():
            pass
    """
    return _create_role_decorator(required_roles=allowed_roles)


def admin_required(fn):
    """
    Decorator to require admin role for a route.
    Shorthand for @roles_required(['admin'])
    """
    return _create_role_decorator(required_roles=['admin'])(fn)


def doctor_required(fn):
    """
    Decorator to require doctor role for a route.
    Shorthand for @roles_required(['doctor'])
    """
    return _create_role_decorator(required_roles=['doctor'])(fn)


def patient_required(fn):
    """
    Decorator to require patient role for a route.
    Shorthand for @roles_required(['patient'])
    """
    return _create_role_decorator(required_roles=['patient'])(fn)


def admin_or_doctor_required(fn):
    """
    Decorator to require admin or doctor role for a route.
    Shorthand for @roles_required(['admin', 'doctor'])
    """
    return _create_role_decorator(required_roles=['admin', 'doctor'])(fn)


def get_current_user_from_request():
    """
    Helper function to get current user in a route.
    Must be called within a route that has already verified JWT.

    Returns:
        User model instance or None
    """
    try:
        identity = get_jwt_identity()
        if identity:
            return User.query.get(int(identity))
        return None
    except Exception:
        return None
