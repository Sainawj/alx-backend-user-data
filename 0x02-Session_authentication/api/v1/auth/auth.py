#!/usr/bin/env python3
"""Module to manage API authentication."""
from typing import List, TypeVar
from flask import request
import os

# Define a TypeVar named User
User = TypeVar('User')


class Auth:
    """Template class for API authentication management."""

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """
        Determines if authentication is required for a given path.

        Args:
            path (str): The path to check.
            excluded_paths (List[str]): A list of paths that do not
            require authentication.

        Returns:
            bool: True if authentication is required, False otherwise.
        """
        if path is None or not excluded_paths:
            return True

        # Ensure path ends with a slash for uniform comparison
        if path[-1] != '/':
            path += '/'

        for excluded_path in excluded_paths:
            # Handle wildcard (*) for prefix matching
            if excluded_path.endswith('*'):
                if path.startswith(excluded_path[:-1]):
                    return False
            else:
                # Add trailing slash if missing for exact match comparison
                if excluded_path[-1] != '/':
                    excluded_path += '/'
                if path == excluded_path:
                    return False

        return True

    def authorization_header(self, request=None) -> str:
        """
        Retrieves the authorization header from the Flask request object.

        Args:
            request (Request): The Flask request object.

        Returns:
            str: The value of the Authorization header,
            or None if it's missing.
        """
        if request is None:
            return None

        # Check if the 'Authorization' header exists
        if 'Authorization' not in request.headers:
            return None

        return request.headers['Authorization']

    def current_user(self, request=None) -> User:
        """
        Retrieves the current user based on the request.

        Args:
            request (Request): The Flask request object.

        Returns:
            User: None for now, as user retrieval is not yet implemented.
        """
        # For now, we assume there's no current user, to be expanded later
        return None

    def session_cookie(self, request=None):
        """
        Retrieves the session cookie value from the request.

        Args:
            request (Request): The Flask request object.

        Returns:
            str: The value of the cookie named _my_session_id,
                 or None if it's not found.
        """
        if request is None:
            return None

        # Get the cookie name from the environment variable SESSION_NAME
        session_name = os.getenv("SESSION_NAME", "_my_session_id")

        # Return the value of the session cookie using .get() to avoid KeyError
        return request.cookies.get(session_name)
