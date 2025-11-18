"""
WSGI entry point for Render deployment.
Gunicorn will use this file to start the Flask application.
"""
from backend.main import app

if __name__ == "__main__":
    app.run()

