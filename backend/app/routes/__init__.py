"""
API Routes for the Hospital Management System.
"""
from .auth import auth_bp


def register_blueprints(app):
    """Register all blueprints with the Flask app."""

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Hospital Management System API is running'}

    # Register authentication routes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')