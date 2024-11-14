#!/usr/bin/env python3
"""
Module implementing session authentication with expiration for the API.
"""
import os
from datetime import datetime, timedelta
from .session_auth import SessionAuth

class SessionExpAuth(SessionAuth):
    """Session authentication class that includes session expiration functionality."""
    
    def __init__(self) -> None:
        """Initialize with session duration from the environment."""
        super().__init__()
        try:
            self.session_duration = int(os.getenv('SESSION_DURATION', '0'))
        except ValueError:
            self.session_duration = 0

    def create_session(self, user_id=None):
        """Create a session with an expiration time."""
        session_id = super().create_session(user_id)
        if not session_id:
            return None
        self.user_id_by_session_id[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now()
        }
        return session_id

    def user_id_for_session_id(self, session_id=None) -> str:
        """Retrieve the user ID for a session, checking for expiration."""
        if session_id is None or session_id not in self.user_id_by_session_id:
            return None
        
        session_info = self.user_id_by_session_id[session_id]
        if self.session_duration <= 0:
            return session_info.get('user_id')
        
        if 'created_at' not in session_info:
            return None
        
        exp_time = session_info['created_at'] + timedelta(seconds=self.session_duration)
        if datetime.now() > exp_time:
            return None
        return session_info.get('user_id')
