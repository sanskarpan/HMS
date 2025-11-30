"""
Hospital Management System Flask Application Factory.
"""
import os
import logging
from flask import Flask, send_from_directory, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .models import db
from .services.cache_service import cache
from backend.config import get_config

logger = logging.getLogger(__name__)

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
    # Get the project root directory (parent of backend/)
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(backend_dir)
    frontend_dir = os.path.join(project_root, 'frontend')

    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder=os.path.join(frontend_dir, 'static'),
        static_url_path='/static'
    )

    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    try:
        cache.init_app(app)
        logger.info(f"Cache initialized with type: {app.config.get('CACHE_TYPE', 'SimpleCache')}")
    except Exception as e:
        logger.warning(f"Redis cache initialization failed, using SimpleCache: {e}")
        app.config['CACHE_TYPE'] = 'SimpleCache'
        cache.init_app(app)

    # Register API blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    # Frontend routes - serve Vue SPA
    @app.route('/')
    def serve_index():
        """Serve the main index.html"""
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/manifest.json')
    def serve_manifest():
        """Serve PWA manifest"""
        return send_from_directory(frontend_dir, 'manifest.json', mimetype='application/json')

    @app.route('/sw.js')
    def serve_sw():
        """Serve service worker"""
        return send_from_directory(frontend_dir, 'sw.js', mimetype='application/javascript')

    @app.route('/offline.html')
    def serve_offline():
        """Serve offline page"""
        return send_from_directory(frontend_dir, 'offline.html')

    @app.route('/src/<path:filename>')
    def serve_src(filename):
        """Serve JavaScript source files from frontend/src/"""
        src_dir = os.path.join(frontend_dir, 'src')
        return send_from_directory(src_dir, filename, mimetype='application/javascript')

    @app.route('/<path:path>')
    def serve_frontend(path):
        """Serve frontend routes - check for actual files first, then SPA routing"""
        # Don't handle API routes here
        if path.startswith('api/'):
            return {'error': 'Not found'}, 404

        # Check if it's an actual file in frontend directory
        file_path = os.path.join(frontend_dir, path)
        if os.path.isfile(file_path):
            # Determine mimetype based on extension
            if path.endswith('.js'):
                return send_from_directory(frontend_dir, path, mimetype='application/javascript')
            elif path.endswith('.css'):
                return send_from_directory(frontend_dir, path, mimetype='text/css')
            elif path.endswith('.json'):
                return send_from_directory(frontend_dir, path, mimetype='application/json')
            elif path.endswith('.png'):
                return send_from_directory(frontend_dir, path, mimetype='image/png')
            elif path.endswith('.ico'):
                return send_from_directory(frontend_dir, path, mimetype='image/x-icon')
            else:
                return send_from_directory(frontend_dir, path)

        # For all other paths, serve index.html (Vue Router handles routing)
        return send_from_directory(frontend_dir, 'index.html')

    # Add cache-control headers to prevent browser caching during development
    @app.after_request
    def add_cache_headers(response):
        """Add headers to prevent browser caching for static files"""
        if request.path.startswith('/src/') or request.path.endswith('.js') or request.path.endswith('.json'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
        return response

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
