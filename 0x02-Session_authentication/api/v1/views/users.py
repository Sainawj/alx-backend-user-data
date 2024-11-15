#!/usr/bin/env python3
""" Module of Users views
"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models.user import User

@app_views.route('/users', methods=['GET'], strict_slashes=False)
def view_all_users() -> str:
    """ GET /api/v1/users
    Return:
      - list of all User objects JSON represented
    """
    all_users = [user.to_json() for user in User.all()]
    return jsonify(all_users)

@app_views.route('/users/me', methods=['GET'], strict_slashes=False)
def get_me() -> str:
    """ GET /api/v1/users/me
    Return:
      - JSON representation of the authenticated User
      - 404 if the authenticated user is None
    """
    if request.current_user is None:
        abort(404)
    return jsonify(request.current_user.to_json())

@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
def view_one_user(user_id: str = None) -> str:
    """ GET /api/v1/users/:id
    Path parameter:
      - User ID
    Return:
      - User object JSON represented
      - 404 if the User ID doesn't exist or is "me" with no authenticated user
    """
    if user_id == "me":
        if request.current_user is None:
            abort(404)  # If no authenticated user, return 404
        return jsonify(request.current_user.to_json())  # Return authenticated user

    if user_id is None:
        abort(404)  # Ensure that user_id is not None

    # Fetch the user by ID
    user = User.get(user_id)
    if user is None:
        abort(404)  # If user not found, return 404
    return jsonify(user.to_json())

@app_views.route('/users/<user_id>', methods=['DELETE'], strict_slashes=False)
def delete_user(user_id: str = None) -> str:
    """ DELETE /api/v1/users/:id
    Path parameter:
      - User ID
    Return:
      - empty JSON if the User has been correctly deleted
      - 404 if the User ID doesn't exist
    """
    if user_id is None:
        abort(404)  # Ensure that user_id is not None
    user = User.get(user_id)
    if user is None:
        abort(404)  # If user not found, return 404
    user.remove()  # Remove the user from the database
    return jsonify({}), 200  # Return empty JSON indicating success

@app_views.route('/users', methods=['POST'], strict_slashes=False)
def create_user() -> str:
    """ POST /api/v1/users/
    JSON body:
      - email
      - password
      - last_name (optional)
      - first_name (optional)
    Return:
      - User object JSON represented
      - 400 if can't create the new User
    """
    rj = None
    error_msg = None
    try:
        rj = request.get_json()  # Parse JSON body
    except Exception as e:
        rj = None
    if rj is None:
        error_msg = "Wrong format"  # If JSON format is invalid, return an error message
    if error_msg is None and rj.get("email", "") == "":
        error_msg = "email missing"  # If email is missing, return an error message
    if error_msg is None and rj.get("password", "") == "":
        error_msg = "password missing"  # If password is missing, return an error message
    if error_msg is None:
        try:
            # Create a new user object and populate it with the provided data
            user = User()
            user.email = rj.get("email")
            user.password = rj.get("password")
            user.first_name = rj.get("first_name")
            user.last_name = rj.get("last_name")
            user.save()  # Save the user to the database
            return jsonify(user.to_json()), 201  # Return the created user in JSON format
        except Exception as e:
            error_msg = "Can't create User: {}".format(e)
    return jsonify({'error': error_msg}), 400  # Return an error if user creation fails

@app_views.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)
def update_user(user_id: str = None) -> str:
    """ PUT /api/v1/users/:id
    Path parameter:
      - User ID
    JSON body:
      - last_name (optional)
      - first_name (optional)
    Return:
      - User object JSON represented
      - 404 if the User ID doesn't exist
      - 400 if can't update the User
    """
    if user_id is None:
        abort(404)  # Ensure that user_id is not None
    user = User.get(user_id)
    if user is None:
        abort(404)  # If user not found, return 404
    rj = None
    try:
        rj = request.get_json()  # Parse JSON body
    except Exception as e:
        rj = None
    if rj is None:
        return jsonify({'error': "Wrong format"}), 400  # If the format is wrong, return 400
    # Update the user fields if the values are provided
    if rj.get('first_name') is not None:
        user.first_name = rj.get('first_name')
    if rj.get('last_name') is not None:
        user.last_name = rj.get('last_name')
    user.save()  # Save the updated user to the database
    return jsonify(user.to_json()), 200  # Return the updated user in JSON format
