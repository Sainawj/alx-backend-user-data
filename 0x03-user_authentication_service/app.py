#!/usr/bin/env python3
"""A simple Flask app with user authentication features.
"""
from flask import Flask, jsonify, request, abort, redirect

from auth import Auth  # Import the Auth class for authentication functionality.

app = Flask(__name__)  # Initialize the Flask application.
AUTH = Auth()  # Create an instance of the Auth class.

@app.route("/", methods=["GET"], strict_slashes=False)
def index() -> str:
    """GET /
    Return:
        - The home page's payload.
    """
    return jsonify({"message": "Bienvenue"})  # Return a welcome message.

@app.route("/users", methods=["POST"], strict_slashes=False)
def users() -> str:
    """POST /users
    Return:
        - The account creation payload.
    """
    email, password = request.form.get("email"), request.form.get("password")  # Retrieve email and password from form data.
    try:
        AUTH.register_user(email, password)  # Attempt to register a new user.
        return jsonify({"email": email, "message": "user created"})  # Return success message if registration is successful.
    except ValueError:
        return jsonify({"message": "email already registered"}), 400  # Return error if email is already registered.

@app.route("/sessions", methods=["POST"], strict_slashes=False)
def login() -> str:
    """POST /sessions
    Return:
        - The account login payload.
    """
    email, password = request.form.get("email"), request.form.get("password")  # Retrieve email and password from form data.
    if not AUTH.valid_login(email, password):  # Validate the user's login credentials.
        abort(401)  # Abort with 401 status code if login fails.
    session_id = AUTH.create_session(email)  # Create a session for the logged-in user.
    response = jsonify({"email": email, "message": "logged in"})  # Return login success message.
    response.set_cookie("session_id", session_id)  # Set session ID in cookies.
    return response

@app.route("/sessions", methods=["DELETE"], strict_slashes=False)
def logout() -> str:
    """DELETE /sessions
    Return:
        - Redirects to home route.
    """
    session_id = request.cookies.get("session_id")  # Retrieve session ID from cookies.
    user = AUTH.get_user_from_session_id(session_id)  # Get user associated with the session ID.
    if user is None:
        abort(403)  # Abort with 403 status code if user is not found.
    AUTH.destroy_session(user.id)  # Destroy the user's session.
    return redirect("/")  # Redirect to the home route.

@app.route("/profile", methods=["GET"], strict_slashes=False)
def profile() -> str:
    """GET /profile
    Return:
        - The user's profile information.
    """
    session_id = request.cookies.get("session_id")  # Retrieve session ID from cookies.
    user = AUTH.get_user_from_session_id(session_id)  # Get user associated with the session ID.
    if user is None:
        abort(403)  # Abort with 403 status code if user is not found.
    return jsonify({"email": user.email})  # Return the user's profile information.

@app.route("/reset_password", methods=["POST"], strict_slashes=False)
def get_reset_password_token() -> str:
    """POST /reset_password
    Return:
        - The user's password reset payload.
    """
    email = request.form.get("email")  # Retrieve email from form data.
    reset_token = None
    try:
        reset_token = AUTH.get_reset_password_token(email)  # Attempt to generate a reset token.
    except ValueError:
        reset_token = None  # Handle case where reset token generation fails.
    if reset_token is None:
        abort(403)  # Abort with 403 status code if reset token is not generated.
    return jsonify({"email": email, "reset_token": reset_token})  # Return reset token.

@app.route("/reset_password", methods=["PUT"], strict_slashes=False)
def update_password() -> str:
    """PUT /reset_password

    Return:
        - The user's password updated payload.
    """
    email = request.form.get("email")  # Retrieve email from form data.
    reset_token = request.form.get("reset_token")  # Retrieve reset token from form data.
    new_password = request.form.get("new_password")  # Retrieve new password from form data.
    is_password_changed = False
    try:
        AUTH.update_password(reset_token, new_password)  # Attempt to update the user's password.
        is_password_changed = True
    except ValueError:
        is_password_changed = False  # Handle case where password update fails.
    if not is_password_changed:
        abort(403)  # Abort with 403 status code if password update fails.
    return jsonify({"email": email, "message": "Password updated"})  # Return password update success message.

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")  # Run the Flask application.
