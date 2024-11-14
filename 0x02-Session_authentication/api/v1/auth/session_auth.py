#!/usr/bin/env python3
"""Session authentication module for the API.
"""
from uuid import uuid4
from flask import request

from .auth import Auth
from models.user import User

class SessionAuth(Auth):
    """SessionAuth class for session-based authentication.
    This is currently an empty class that inherits from Auth.
    """
    pass
