#!/usr/bin/env python3
"""A simple end-to-end (E2E) integration test for `app.py`."""

import requests

# Test credentials and base URL for the API
EMAIL = "guillaume@holberton.io"  # Test email
PASSWD = "b4l0u"                  # Test password
NEW_PASSWD = "t4rt1fl3tt3"        # New password for reset test
BASE_URL = "http://0.0.0.0:5000"  # Base URL of the API


def register_user(email: str, password: str) -> None:
    """Tests registering a user."""
    url = "{}/users".format(BASE_URL)  # Endpoint for user registration
    body = {'email': email, 'password': password}

    # Test successful registration
    res = requests.post(url, data=body)
    assert res.status_code == 200
    assert res.json() == {"email": email, "message": "user created"}

    # Test registration with an already registered email
    res = requests.post(url, data=body)
    assert res.status_code == 400
    assert res.json() == {"message": "email already registered"}


def log_in_wrong_password(email: str, password: str) -> None:
    """Tests logging in with a wrong password."""
    url = "{}/sessions".format(BASE_URL)  # Endpoint for login
    body = {'email': email, 'password': password}

    # Test login with incorrect password
    res = requests.post(url, data=body)
    assert res.status_code == 401  # Unauthorized


def log_in(email: str, password: str) -> str:
    """Tests logging in."""
    url = "{}/sessions".format(BASE_URL)  # Endpoint for login
    body = {'email': email, 'password': password}
 
    # Test successful login
    res = requests.post(url, data=body)
    assert res.status_code == 200
    assert res.json() == {"email": email, "message": "logged in"}

    # Return session_id from cookies for further authenticated actions
    return res.cookies.get('session_id')


def profile_unlogged() -> None:
    """Tests retrieving profile information whilst logged out."""
    url = "{}/profile".format(BASE_URL)  # Endpoint for profile access
  
    # Test profile access without being logged in
    res = requests.get(url)
    assert res.status_code == 403  # Forbidden


def profile_logged(session_id: str) -> None:
    """Tests retrieving profile information whilst logged in."""
    url = "{}/profile".format(BASE_URL)  # Endpoint for profile access
    req_cookies = {'session_id': session_id}

    # Test profile access with valid session
    res = requests.get(url, cookies=req_cookies)
    assert res.status_code == 200
    assert "email" in res.json()


def log_out(session_id: str) -> None:
    """Tests logging out of a session."""
    url = "{}/sessions".format(BASE_URL)  # Endpoint for logout
    req_cookies = {'session_id': session_id}
  
    # Test session termination
    res = requests.delete(url, cookies=req_cookies)
    assert res.status_code == 200
    assert res.json() == {"message": "Bienvenue"}


def reset_password_token(email: str) -> str:
    """Tests requesting a password reset."""
    url = "{}/reset_password".format(BASE_URL)
    body = {'email': email}
 
    # Test successful reset token generation
    res = requests.post(url, data=body)
    assert res.status_code == 200
    assert "email" in res.json()
    assert res.json()["email"] == email
    assert "reset_token" in res.json()
 
    # Return reset token for further actions
    return res.json().get('reset_token')


def update_password(
    email: str, reset_token: str, new_password: str
    ) -> None:
    """Tests updating a user's password."""
    url = "{}/reset_password".format(BASE_URL)  # Endpoint
    body = {
        'email': email,
        'reset_token': reset_token,
        'new_password': new_password,
    }

    # Test successful password update
    res = requests.put(url, data=body)
    assert res.status_code == 200
    assert res.json() == {"email": email, "message": "Password updated"}


if __name__ == "__main__":
    # Run the tests in sequence to verify the entire user lifecycle
    register_user(EMAIL, PASSWD)                   # Register a new user
    log_in_wrong_password(EMAIL, NEW_PASSWD)      # Test login
    profile_unlogged()                            # Test profile access
    session_id = log_in(EMAIL, PASSWD)            # Log in and get session ID
    profile_logged(session_id)                    # Access while logged in
    log_out(session_id)                           # Log out
    reset_token = reset_password_token(EMAIL)     # req. password reset token
    update_password(EMAIL, reset_token, NEW_PASSWD)  # Update the password
    log_in(EMAIL, NEW_PASSWD)                     # Log in with the new password
