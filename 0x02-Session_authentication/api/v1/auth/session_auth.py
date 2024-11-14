#!/usr/bin/env python3
"""Session authentication module for the API.
"""
from uuid import uuid4
from .auth import Auth

class SessionAuth(Auth):
    """SessionAuth class for session-based authentication.
    """
    # Class attribute to store user IDs by session ID
    user_id_by_session_id = {}

    def create_session(self, user_id: str = None) -> str:
        """Creates a Session ID for a given user_id.
        
        Args:
            user_id (str): The user ID to create a session for.
            
        Returns:
            str: The created Session ID, or None if user_id is None or not a string.
        """
        if user_id is None or not isinstance(user_id, str):
            return None

        # Generate a new session ID
        session_id = str(uuid4())

        # Store the session ID with the user ID
        self.user_id_by_session_id[session_id] = user_id

        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """Returns a User ID based on a Session ID.
        
        Args:
            session_id (str): The session ID to retrieve the user ID for.
            
        Returns:
            str: The user ID associated with the session ID, or None if invalid.
        """
        if session_id is None or not isinstance(session_id, str):
            return None

        # Retrieve the user ID using the session ID
        return self.user_id_by_session_id.get(session_id)
