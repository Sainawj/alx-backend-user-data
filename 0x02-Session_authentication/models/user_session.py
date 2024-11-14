#!/usr/bin/env python3
"""
UserSession model for storing session information in the database (file).
"""

from models.base import Base


class UserSession(Base):
    """Represents a user session stored in the database."""
    def __init__(self, *args: list, **kwargs: dict):
        """Initialize UserSession with user_id and session_id."""
        super().__init__(*args, **kwargs)
        self.user_id = kwargs.get("user_id")
        self.session_id = kwargs.get("session_id")
