#!/usr/bin/env python3
"""Module implementing session authentication with expiration for the API.
"""
import os
from flask import request
from datetime import datetime, timedelta

from .session_auth import SessionAuth


class SessionExpAuth(SessionAuth):
    """Session authentication class that includes session expiration functionality.
    """

    def __init__(self) -> None:
        """Initializes a new instance of SessionExpAuth and sets session duration.
        
        Retrieves session duration from environment variables. Defaults to 0 if not set.
        """
        super().__init__()
        try:
            # Get session duration from the environment; default to 0 if not provided
            self.session_duration = int(os.getenv('SESSION_DURATION', '0'))
        except Exception:
            self.session_duration = 0

    def create_session(self, user_id=None):
        """Creates a session ID for the specified user and stores the session with a timestamp.
        
        Parameters:
          - user_id (str): The ID of the user for whom the session is created.

        Returns:
          - str: The generated session ID or None if session creation fails.
        """
        # Generate a session ID using the parent class method
        session_id = super().create_session(user_id)
        if type(session_id) != str:
            return None
        # Store session details, including the timestamp for session expiration tracking
        self.user_id_by_session_id[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),  # Record the session creation time
        }
        return session_id

    def user_id_for_session_id(self, session_id=None) -> str:
        """Retrieves the user ID associated with a valid (non-expired) session ID.
        
        Parameters:
          - session_id (str): The session ID to check.

        Returns:
          - str: The user ID if session is valid and not expired, None otherwise.
        """
        # Check if session ID exists in the session dictionary
        if session_id in self.user_id_by_session_id:
            session_dict = self.user_id_by_session_id[session_id]
            
            # Return the user ID immediately if no expiration is set
            if self.session_duration <= 0:
                return session_dict['user_id']
            
            # Ensure the session has a valid creation timestamp
            if 'created_at' not in session_dict:
                return None
            
            # Calculate expiration time based on session duration
            cur_time = datetime.now()
            time_span = timedelta(seconds=self.session_duration)
            exp_time = session_dict['created_at'] + time_span
            
            # Return None if the session has expired
            if exp_time < cur_time:
                return None
            
            # Return the user ID if session is still valid
            return session_dict['user_id']
