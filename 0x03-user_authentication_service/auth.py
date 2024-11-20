#!/usr/bin/env python3
"""A module for authentication-related routines.
"""
import bcrypt  # Library for password hashing.
from uuid import uuid4  # Used to generate unique session and reset tokens.
from typing import Union  # Enables type hints for functions returning multiple types.
from sqlalchemy.orm.exc import NoResultFound  # Exception for missing database records.

from db import DB  # Import the database interface.
from user import User  # Import the User model.


def _hash_password(password: str) -> bytes:
    """Hashes a password.
    
    Args:
        password (str): The plaintext password to hash.
    
    Returns:
        bytes: The hashed password.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def _generate_uuid() -> str:
    """Generates a UUID.
    
    Returns:
        str: A newly generated UUID as a string.
    """
    return str(uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        """Initializes a new Auth instance.
        """
        self._db = DB()  # Initialize a database instance.

    def register_user(self, email: str, password: str) -> User:
        """Adds a new user to the database.
        
        Args:
            email (str): The user's email address.
            password (str): The user's plaintext password.
        
        Returns:
            User: The newly created user instance.
        
        Raises:
            ValueError: If the email is already registered.
        """
        try:
            self._db.find_user_by(email=email)  # Check if user already exists.
        except NoResultFound:
            return self._db.add_user(email, _hash_password(password))  # Add new user.
        raise ValueError("User {} already exists".format(email))  # Raise error if user exists.

    def valid_login(self, email: str, password: str) -> bool:
        """Checks if a user's login details are valid.
        
        Args:
            email (str): The user's email.
            password (str): The user's plaintext password.
        
        Returns:
            bool: True if login is valid, otherwise False.
        """
        user = None
        try:
            user = self._db.find_user_by(email=email)  # Fetch user by email.
            if user is not None:
                return bcrypt.checkpw(
                    password.encode("utf-8"),
                    user.hashed_password,
                )  # Compare hashed passwords.
        except NoResultFound:
            return False  # Return False if user does not exist.
        return False

    def create_session(self, email: str) -> str:
        """Creates a new session for a user.
        
        Args:
            email (str): The user's email address.
        
        Returns:
            str: The session ID for the user.
        """
        user = None
        try:
            user = self._db.find_user_by(email=email)  # Fetch user by email.
        except NoResultFound:
            return None  # Return None if user does not exist.
        if user is None:
            return None
        session_id = _generate_uuid()  # Generate a unique session ID.
        self._db.update_user(user.id, session_id=session_id)  # Update user with session ID.
        return session_id

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """Retrieves a user based on a given session ID.
        
        Args:
            session_id (str): The session ID associated with the user.
        
        Returns:
            Union[User, None]: The user instance or None if not found.
        """
        user = None
        if session_id is None:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)  # Fetch user by session ID.
        except NoResultFound:
            return None  # Return None if session is invalid.
        return user

    def destroy_session(self, user_id: int) -> None:
        """Destroys a session associated with a given user.
        
        Args:
            user_id (int): The user's ID.
        """
        if user_id is None:
            return None
        self._db.update_user(user_id, session_id=None)  # Remove session ID from user.

    def get_reset_password_token(self, email: str) -> str:
        """Generates a password reset token for a user.
        
        Args:
            email (str): The user's email address.
        
        Returns:
            str: The generated reset token.
        
        Raises:
            ValueError: If the user does not exist.
        """
        user = None
        try:
            user = self._db.find_user_by(email=email)  # Fetch user by email.
        except NoResultFound:
            user = None
        if user is None:
            raise ValueError()  # Raise error if user does not exist.
        reset_token = _generate_uuid()  # Generate a unique reset token.
        self._db.update_user(user.id, reset_token=reset_token)  # Update user with reset token.
        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """Updates a user's password given the user's reset token.
        
        Args:
            reset_token (str): The user's reset token.
            password (str): The new plaintext password.
        
        Raises:
            ValueError: If the reset token is invalid.
        """
        user = None
        try:
            user = self._db.find_user_by(reset_token=reset_token)  # Fetch user by reset token.
        except NoResultFound:
            user = None
        if user is None:
            raise ValueError()  # Raise error if reset token is invalid.
        new_password_hash = _hash_password(password)  # Hash the new password.
        self._db.update_user(
            user.id,
            hashed_password=new_password_hash,
            reset_token=None,  # Remove reset token after password update.
        )