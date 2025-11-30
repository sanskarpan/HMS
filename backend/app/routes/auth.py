"""
Auth routes - login, registration, logout, token management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token
)
from datetime import datetime

from backend.app.models import db, User, Patient
from backend.app.utils import (
    create_auth_response,
    validate_login_credentials,
    login_required,
    get_current_user_from_request
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login for admin, doctor, or patient accounts."""
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'message': 'No data provided',
            'error': 'bad_request'
        }), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({
            'success': False,
            'message': 'Username and password are required',
            'error': 'missing_credentials'
        }), 400

    user, error = validate_login_credentials(username, password)

    if error:
        return jsonify({
            'success': False,
            'message': error,
            'error': 'invalid_credentials'
        }), 401

    response = create_auth_response(user, "Login successful")
    return jsonify(response), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new patient account. Doctors/admins cannot self-register."""
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'message': 'No data provided',
            'error': 'bad_request'
        }), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()

    errors = []
    if not username:
        errors.append('Username is required')
    if not email:
        errors.append('Email is required')
    if not password:
        errors.append('Password is required')
    if not full_name:
        errors.append('Full name is required')
    if not phone:
        errors.append('Phone number is required')

    if errors:
        return jsonify({
            'success': False,
            'message': 'Validation failed',
            'errors': errors
        }), 400

    if len(username) < 3:
        errors.append('Username must be at least 3 characters')

    if len(password) < 6:
        errors.append('Password must be at least 6 characters')

    if '@' not in email or '.' not in email:
        errors.append('Invalid email format')

    if errors:
        return jsonify({
            'success': False,
            'message': 'Validation failed',
            'errors': errors
        }), 400

    if User.find_by_username(username):
        return jsonify({
            'success': False,
            'message': 'Username already exists',
            'error': 'username_taken'
        }), 409

    if User.find_by_email(email):
        return jsonify({
            'success': False,
            'message': 'Email already registered',
            'error': 'email_taken'
        }), 409

    try:
        user = User(
            username=username,
            email=email,
            password=password,
            role='patient'
        )
        db.session.add(user)
        db.session.flush()

        date_of_birth = None
        if data.get('date_of_birth'):
            try:
                date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                pass

        patient = Patient(
            user_id=user.id,
            full_name=full_name,
            phone=phone,
            date_of_birth=date_of_birth,
            gender=data.get('gender'),
            address=data.get('address'),
            blood_group=data.get('blood_group'),
            emergency_contact=data.get('emergency_contact'),
            medical_history=data.get('medical_history')
        )
        db.session.add(patient)
        db.session.commit()

        response = create_auth_response(user, "Registration successful")
        return jsonify(response), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'error': str(e)
        }), 500


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user_info():
    """Fetch info for the logged-in user."""
    user = get_current_user_from_request()

    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found',
            'error': 'user_not_found'
        }), 401

    return jsonify({
        'success': True,
        'user': user.to_dict(include_profile=True)
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Generate new access token using refresh token."""
    identity = get_jwt_identity()

    user = User.query.get(int(identity))
    if not user or not user.can_login:
        return jsonify({
            'success': False,
            'message': 'User not found or inactive',
            'error': 'invalid_user'
        }), 401

    new_access_token = create_access_token(
        identity=identity,
        additional_claims={
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    )

    return jsonify({
        'success': True,
        'access_token': new_access_token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Handle logout. JWT logout is client-side (token removal),
    but this endpoint exists for API consistency.
    """
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Update password for the authenticated user."""
    user = get_current_user_from_request()
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'message': 'No data provided',
            'error': 'bad_request'
        }), 400

    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not current_password or not new_password:
        return jsonify({
            'success': False,
            'message': 'Both current and new password required',
            'error': 'missing_fields'
        }), 400

    if len(new_password) < 6:
        return jsonify({
            'success': False,
            'message': 'New password must be at least 6 characters',
            'error': 'password_too_short'
        }), 400

    if not user.check_password(current_password):
        return jsonify({
            'success': False,
            'message': 'Current password is incorrect',
            'error': 'invalid_password'
        }), 401

    user.set_password(new_password)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Password changed successfully'
    }), 200
