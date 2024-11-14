#!/usr/bin/env python3
"""Session Authentication Views for the API."""

from flask import jsonify, request, make_response
from api.v1.views import app_views
from models.user import User
from api.v1.app import auth


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def login():
    """Handles POST request for /auth_session/login."""
    email = request.form.get("email")
    password = request.form.get("password")

    # Check if email or password is missing
    if not email:
        return jsonify({"error": "email missing"}), 400
    if not password:
        return jsonify({"error": "password missing"}), 400

    # Find the user based on the provided email
    user = User.search({"email": email})
    if not user:
        return jsonify({"error": "no user found for this email"}), 404

    # Check if the provided password is valid
    if not user[0].is_valid_password(password):
        return jsonify({"error": "wrong password"}), 401

    # Create a session ID for the user
    session_id = auth.create_session(user[0].id)

    # Get user JSON representation and send it back
    user_json = user[0].to_json()

    # Set the session cookie
    response = make_response(jsonify(user_json))
    response.set_cookie(auth.SESSION_NAME, session_id)

    return response
