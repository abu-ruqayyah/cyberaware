"""
CyberAware WSGI Entry Point for Production Deployment
Suitable for deployment with Gunicorn, Waitress, or uWSGI.
"""

from app import create_app
from run import seed_database

app = create_app()

# Initialize schema on startup if not already created
seed_database()

if __name__ == "__main__":
    app.run()
