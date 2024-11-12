#!/usr/bin/env python3
"""Module for Basic API authentication."""
from api.v1.auth.auth import Auth
import base64

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
        
        if ':' not in decoded_base64_authorization_header:
            return None, None
        
        # Split the string by the colon and return the user email and password
        email, password = decoded_base64_authorization_header.split(":", 1)
        return email, password
