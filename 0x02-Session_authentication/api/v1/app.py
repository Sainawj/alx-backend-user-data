#!/usr/bin/env python3
"""
Route module for the API
"""
from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import CORS
from api.v1.auth.auth import Auth
from api.v1.auth.basic_auth import BasicAuth

# Attempt to import SessionAuth and SessionExpAuth
try:
    from api.v1.auth.session_auth import SessionAuth
except ImportError:
    SessionAuth = None

try:
    from api.v1.auth.session_exp_auth import SessionExpAuth
except ImportError:
    SessionExpAuth = None

app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Initialize auth to None
auth = None

# Get the authentication type from environment variable
auth_type = getenv("AUTH_TYPE")

# Determine which authentication type to use
if auth_type == "basic_auth":
    auth = BasicAuth()
elif auth_type == "session_auth" and SessionAuth is not None:
    auth = SessionAuth()
elif auth_type == "session_exp_auth" and SessionExpAuth is not None:
    auth = SessionExpAuth()
else:
    auth = Auth()


@app.before_request
def before_request():
    """
    Filters each incoming request to check if authentication is required.
    If authentication is required, it checks for the authorization header and user.
    """
    if auth is None:
        return None

    # List of routes that do not require authentication
    excluded_paths = [
        '/api/v1/status/',
        '/api/v1/unauthorized/',
        '/api/v1/forbidden/',
        '/api/v1/auth_session/login/'
    ]

    # Check if the path requires authentication
    if auth.require_auth(request.path, excluded_paths):
        # Check for authorization header or session cookie
        if auth.authorization_header(request) is None and auth.session_cookie(request) is None:
            abort(401)  # Unauthorized error

        # Set the current_user attribute
        request.current_user = auth.current_user(request)

        # If no current user, abort with Forbidden error
        if request.current_user is None:
            abort(403)  # Forbidden error


@app.errorhandler(404)
def not_found(error) -> str:
    """Not found handler."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error) -> str:
    """Unauthorized handler."""
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> str:
    """Forbidden handler."""
    return jsonify({"error": "Forbidden"}), 403


if __name__ == "__main__":
    # Get host and port from environment, defaulting to "0.0.0.0" and "5000"
    host = getenv("API_HOST", "0.0.0.0")
    port = int(getenv("API_PORT", "5000"))
    app.run(host=host, port=port)
