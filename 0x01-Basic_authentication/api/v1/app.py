#!/usr/bin/env python3
"""App module to run the API with request validation."""

from flask import Flask, jsonify, abort, request
from flask_cors import CORS
from os import getenv

from api.v1.auth.auth import Auth  # Import the Auth class

app = Flask(__name__)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Initialize the auth instance
auth = None
auth_type = getenv("AUTH_TYPE", None)

if auth_type == "auth":
    auth = Auth()

@app.before_request
def before_request():
    """
    Filter each request to secure the API.
    """
    if auth is None:
        return

    # List of paths that don't require authentication
    excluded_paths = ['/api/v1/status/', '/api/v1/unauthorized/', '/api/v1/forbidden/']

    # Validate if path requires authentication
    if not auth.require_auth(request.path, excluded_paths):
        return

    # Check if the request has an Authorization header
    if auth.authorization_header(request) is None:
        abort(401)

    # Check if the current user is authenticated
    if auth.current_user(request) is None:
        abort(403)

# Endpoint for checking API status
@app.route('/api/v1/status/', methods=['GET'])
def status():
    """Returns the status of the API."""
    return jsonify({"status": "OK"})

# Unauthorized error handler
@app.errorhandler(401)
def unauthorized_error(error):
    """Handles 401 Unauthorized errors."""
    return jsonify({"error": "Unauthorized"}), 401

# Forbidden error handler
@app.errorhandler(403)
def forbidden_error(error):
    """Handles 403 Forbidden errors."""
    return jsonify({"error": "Forbidden"}), 403
