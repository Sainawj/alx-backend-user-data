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

# Import SessionAuth if the file exists
try:
    from api.v1.auth.session_auth import SessionAuth
except ImportError:
    SessionAuth = None

# Import SessionExpAuth if the file exists
try:
    from api.v1.auth.session_exp_auth import SessionExpAuth
except ImportError:
    SessionExpAuth = None

# Import SessionDBAuth if the file exists
try:
    from api.v1.auth.session_db_auth import SessionDBAuth
except ImportError:
    SessionDBAuth = None

app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Initialize auth to None
auth = None

# Set up authentication type based on the AUTH_TYPE environment variable
auth_type = getenv("AUTH_TYPE")

if auth_type == "basic_auth":
    auth = BasicAuth()
elif auth_type == "session_auth" and SessionAuth is not None:
    auth = SessionAuth()
elif auth_type == "session_exp_auth" and SessionExpAuth is not None:
    auth = SessionExpAuth()
elif auth_type == "session_db_auth" and SessionDBAuth is not None:
    auth = SessionDBAuth()
else:
    auth = Auth()


@app.before_request
def before_request():
    """
    Filters each incoming request to check if authentication is required.
    """
    if auth is None:
        return None

    excluded_paths = [
        '/api/v1/status/', '/api/v1/unauthorized/', '/api/v1/forbidden/',
        '/api/v1/auth_session/login/'  # Exclude this route from auth
    ]

    if auth.require_auth(request.path, excluded_paths):
        if auth.authorization_header(request) is None and auth.session_cookie(request) is None:
            abort(401)  # Unauthorized error

        request.current_user = auth.current_user(request)
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


@app.route('/api/v1/users/me', methods=['GET'])
def get_current_user():
    """
    Retrieve the authenticated User object.
    """
    if request.current_user is None:
        abort(404)  # User not found
    return jsonify(request.current_user.to_dict()), 200


@app.route('/api/v1/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Retrieve a User by ID or the current authenticated User.
    """
    if user_id == "me":
        if request.current_user is None:
            abort(404)  # User not found
        return jsonify(request.current_user.to_dict()), 200

    # Otherwise, proceed with normal user lookup
    user = User.get(user_id)  # Assuming a method that fetches a User by ID
    if user is None:
        abort(404)  # User not found
    return jsonify(user.to_dict()), 200


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)
