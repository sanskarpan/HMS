"""
API Routes for the Hospital Management System.
"""


def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Hospital Management System API is running'}
    pass
