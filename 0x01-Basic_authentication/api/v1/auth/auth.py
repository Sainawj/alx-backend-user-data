#!/usr/bin/env python3
"""Module to manage API authentication."""
from typing import List, TypeVar
from flask import request

class Auth:
    """
    Auth class to manage API authentication.
    """

    
    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """
        Determines if a path requires authentication based on excluded paths.

        Args:
            path (str): The path to check.
            excluded_paths (List[str]): A list of paths that don't require authentication.

        Returns:
            bool: True if authentication is required, False otherwise.
        """
        if path is None or excluded_paths is None or len(excluded_paths) == 0:
            return True

        # Add trailing slashes to paths for consistent comparison
        if not path.endswith('/'):
            path += '/'
        
        # Normalize excluded_paths for consistent comparison
        normalized_excluded_paths = [p if p.endswith('/') else p + '/' for p in excluded_paths]

        return path not in normalized_excluded_paths

    
    def authorization_header(self, request=None) -> str:
        """
        Retrieves the Authorization header from the request.

        Args:
            request (Request): The Flask request object.

        Returns:
            str: The Authorization header value, or None if not present.
        """
        if request is None:
            return None
        return request.headers.get("Authorization")

    
    def current_user(self, request=None) -> TypeVar('User'):
        """
        Placeholder method for retrieving the current user.

        Args:
            request (Request): The Flask request object.

        Returns:
            TypeVar('User'): None (for now, as this will be implemented later).
        """
        return None
