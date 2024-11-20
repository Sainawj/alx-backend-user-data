#!/usr/bin/env python3
"""The `user` model's module.
Defines the database model for the `users` table.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Create a base class for declarative class definitions
Base = declarative_base()


class User(Base):
    """Represents a record from the `users` table.
    
    This class maps the `users` table in the database and defines its schema.
    """
    __tablename__ = "users"  # Name of the table in the database

    # Unique identifier for each user (Primary Key)
    id = Column(Integer, primary_key=True)
    
    # User's email address (required and unique)
    email = Column(String(250), nullable=False)
    
    # Hashed password for user authentication (required)
    hashed_password = Column(String(250), nullable=False)
    
    # Optional session ID for tracking active sessions
    session_id = Column(String(250), nullable=True)
    
    # Optional token used for password reset requests
    reset_token = Column(String(250), nullable=True)