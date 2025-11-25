"""
Hospital Management System Flask Application Factory.
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .models import db
from backend.config import get_config


# Initialize extensions
jwt = JWTManager()


def create_app(config_class=None):
    """
    Application factory for creating Flask app instances.

    Args:
        config_class: Configuration class to use. Defaults to environment-based config.

    Returns:
        Flask application instance
    """
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Handle expired tokens."""
    return {
        'success': False,
        'message': 'Token has expired',
        'error': 'token_expired'
    }, 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Handle invalid tokens."""
    return {
        'success': False,
        'message': 'Invalid token',
        'error': 'invalid_token'
    }, 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    """Handle missing tokens."""
    return {
        'success': False,
        'message': 'Authorization token is required',
        'error': 'authorization_required'
    }, 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    """Handle revoked tokens."""
    return {
        'success': False,
        'message': 'Token has been revoked',
        'error': 'token_revoked'
    }, 401
