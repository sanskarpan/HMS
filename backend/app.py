"""
Main entry point for the Hospital Management System Flask application.
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Run the development server
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
