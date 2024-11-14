#!/usr/bin/env python3
"""
SessionDBAuth module that uses database storage for session information.
"""

from .session_exp_auth import SessionExpAuth
from models.user_session import UserSession
from datetime import datetime


class SessionDBAuth(SessionExpAuth):
    """Session authentication with session data stored in the database."""

    def create_session(self, user_id=None):
        """Create and store a new session in the database."""
        session_id = super().create_session(user_id)
        if not session_id:
            return None

        # Create a new UserSession and save it
        user_session = UserSession(user_id=user_id, session_id=session_id)
        user_session.save()
        return session_id

    def user_id_for_session_id(self, session_id=None):
        """Retrieve the User ID from the database for a given session_id."""
        if session_id is None:
            return None

        UserSession.load_from_file()  # Load sessions from the database
        user_sessions = UserSession.all()
        
        for session in user_sessions.values():
            if session.session_id == session_id:
                # Check expiration if session_duration is set
                if self.session_duration > 0:
                    created_at = session.created_at
                    expiration_time = created_at + timedelta(seconds=self.session_duration)
                    if datetime.now() > expiration_time:
                        return None
                return session.user_id
        return None

    def destroy_session(self, request=None):
        """Destroy a session in the database based on the Session ID."""
        if request is None:
            return False
        session_id = self.session_cookie(request)
        if not session_id:
            return False

        # Load the UserSession and delete it if it exists
        UserSession.load_from_file()
        user_sessions = UserSession.all()
        
        for session_key, session in user_sessions.items():
            if session.session_id == session_id:
                session.delete()
                return True
        return False
