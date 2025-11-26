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


