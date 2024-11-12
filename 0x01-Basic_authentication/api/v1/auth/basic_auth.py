#!/usr/bin/env python3
"""Module for Basic API authentication."""
from api.v1.auth.auth import Auth
import base64
from typing import TypeVar
from models.user import User

class BasicAuth(Auth):
    """BasicAuth class inherits from Auth."""


    def extract_base64_authorization_header(self, authorization_header: str) -> str:
        """
        Extracts the Base64 part of the Authorization header for Basic Authentication.

        Args:
            authorization_header (str): The Authorization header to process.

        Returns:
            str: The Base64 part of the Authorization header, or None if invalid.
        """
        if authorization_header is None:
            return None
        
        if not isinstance(authorization_header, str):
            return None
        
        if not authorization_header.startswith("Basic "):
            return None
        
        # Return the Base64 part after 'Basic ' (i.e., the part after the space)
        return authorization_header.split("Basic ")[1]


    def decode_base64_authorization_header(self, base64_authorization_header: str) -> str:
        """
        Decodes the Base64 authorization header.

        Args:
            base64_authorization_header (str): The Base64 string to decode.

        Returns:
            str: The decoded string in UTF-8, or None if invalid.
        """
        if base64_authorization_header is None:
            return None
        
        if not isinstance(base64_authorization_header, str):
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

    Args:
        decoded_base64_authorization_header (str): The decoded Base64 string containing email and password.

    Returns:
        tuple: A tuple with the user email and password, or (None, None) if invalid.
    """
    if decoded_base64_authorization_header is None:
        return None, None

    if not isinstance(decoded_base64_authorization_header, str):
        return None, None

    # Use split only once on the first colon
    if ':' not in decoded_base64_authorization_header:
        return None, None
    
    email, password = decoded_base64_authorization_header.split(":", 1)
    return email, password


    def user_object_from_credentials(self, user_email: str, user_pwd: str) -> TypeVar('User'):
        """
        Returns the User instance based on email and password.

        Args:
            user_email (str): The user's email address.
            user_pwd (str): The user's password.

        Returns:
            User: The User instance if credentials are valid, or None otherwise.
        """
        # Check if user_email and user_pwd are valid strings
        if user_email is None or not isinstance(user_email, str):
            return None
        if user_pwd is None or not isinstance(user_pwd, str):
            return None

        # Search for the user by email
        users = User.search({'email': user_email})
        if not users or len(users) == 0:
            return None

        # Validate the password
        user = users[0]
        if not user.is_valid_password(user_pwd):
            return None

        # Return the User instance if valid
        return user

    def current_user(self, request=None) -> TypeVar('User'):
        """
        Retrieves the User instance for a request based on Basic Authentication.

        Args:
            request: The request object.

        Returns:
            User: The User instance if authentication is successful, or None otherwise.
        """
        # Retrieve the Authorization header from the request
        authorization_header = self.authorization_header(request)
        if authorization_header is None:
            return None

        # Extract, decode, and retrieve user credentials
        base64_auth_header = self.extract_base64_authorization_header(authorization_header)
        decoded_auth_header = self.decode_base64_authorization_header(base64_auth_header)
        user_email, user_pwd = self.extract_user_credentials(decoded_auth_header)

        # Retrieve the User object based on the email and password
        return self.user_object_from_credentials(user_email, user_pwd)
