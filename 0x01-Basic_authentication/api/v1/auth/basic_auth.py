#!/usr/bin/env python3
"""Module for Basic API authentication."""
import base64
from typing import Type
from models.user import User  # Assuming User model is imported


class BasicAuth(Auth):
    """BasicAuth class inherits from Auth."""

    
    def extract_base64_authorization_header(self, authorization_header: str) -> str:
        """
        Extracts the Base64 part of the Authorization header for Basic Authentication.
        """
        if authorization_header is None or not isinstance(authorization_header, str):
            return None

        if not authorization_header.startswith("Basic "):
            return None

        # Return the Base64 part after 'Basic ' (i.e., the part after the space)
        return authorization_header.split("Basic ")[1]

    
    def decode_base64_authorization_header(self, base64_authorization_header: str) -> str:
        """
        Decodes the Base64 authorization header.
        """
        if base64_authorization_header is None or not isinstance(base64_authorization_header, str):
            return None

        try:
            # Decode the Base64 string and return the result as a UTF-8 string
            decoded_bytes = base64.b64decode(base64_authorization_header)
            return decoded_bytes.decode('utf-8')
        except (base64.binascii.Error, UnicodeDecodeError):
            return None

    
    def extract_user_credentials(self, decoded_base64_authorization_header: str) -> (str, str):
        """
        Extracts the user credentials (email and password) from the decoded Base64 authorization header.
        """
        if not isinstance(decoded_base64_authorization_header, str) or ':' not in decoded_base64_authorization_header:
            return None, None

        # Split the string by the colon and return the user email and password
        email, password = decoded_base64_authorization_header.split(":", 1)
        return email, password

    
    def user_object_from_credentials(self, user_email: str, user_pwd: str) -> Type[User]:
        """
        Retrieves the User instance based on user_email and user_pwd.

        Args:
            user_email (str): The user's email address.
            user_pwd (str): The user's password.

        Returns:
            User: The corresponding User instance if credentials are valid, otherwise None.
        """
        if not isinstance(user_email, str) or not isinstance(user_pwd, str) or user_email is None or user_pwd is None:
            return None

        # Use the search method of User to find the user based on the email
        users = User.search({"email": user_email})

        if not users:
            return None

        # Assume the search method returns a list of users, and we take the first one
        user = users[0]

        # Check if the password is valid for the found user
        if not user.is_valid_password(user_pwd):
            return None

        return user
