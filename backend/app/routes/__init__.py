"""
API Routes for the Hospital Management System.
"""
from .auth import auth_bp
from .admin import admin_bp
from .doctor import doctor_bp
from .patient import patient_bp
from .payment import payment_bp
from .reports import reports_bp


def register_blueprints(app):
    """Register all blueprints with the Flask app."""

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Hospital Management System API is running'}

    # Register authentication routes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Register admin routes
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Register doctor routes
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')

    # Register patient routes
    app.register_blueprint(patient_bp, url_prefix='/api/patient')

    # Register payment routes
    app.register_blueprint(payment_bp, url_prefix='/api/payment')

    # Register reports routes
    app.register_blueprint(reports_bp, url_prefix='/api/reports')