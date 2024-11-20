#!/usr/bin/env python3
"""DB module.
"""
from sqlalchemy import create_engine, tuple_  # For SQLAlchemy engine creation and tuple filtering.
from sqlalchemy.exc import InvalidRequestError  # Raised for invalid query fields.
from sqlalchemy.ext.declarative import declarative_base  # Base class for ORM models.
from sqlalchemy.orm import sessionmaker  # Used to create database sessions.
from sqlalchemy.orm.exc import NoResultFound  # Raised when a query result is empty.
from sqlalchemy.orm.session import Session  # Type hint for database sessions.

from user import Base, User  # Import ORM base and User model.


class DB:
    """DB class for managing database operations.
    """

    def __init__(self) -> None:
        """Initialize a new DB instance.
        
        Sets up the database engine and initializes the schema.
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)  # Create SQLite database.
        Base.metadata.drop_all(self._engine)  # Drop all tables (for a fresh start).
        Base.metadata.create_all(self._engine)  # Create all tables.
        self.__session = None  # Session object (lazy initialization).

    @property
    def _session(self) -> Session:
        """Memoized session object for database interactions.
        
        Returns:
            Session: A SQLAlchemy session object.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)  # Bind session to engine.
            self.__session = DBSession()  # Create a session instance.
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Adds a new user to the database.
        
        Args:
            email (str): The email address of the user.
            hashed_password (str): The hashed password of the user.
        
        Returns:
            User: The newly added user object or None if the operation fails.
        """
        try:
            new_user = User(email=email, hashed_password=hashed_password)  # Create a new user instance.
            self._session.add(new_user)  # Add user to the session.
            self._session.commit()  # Commit the session.
        except Exception:  # Rollback on failure.
            self._session.rollback()
            new_user = None
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """Finds a user based on a set of filters.
        
        Args:
            **kwargs: Arbitrary keyword arguments representing filters (e.g., email="example@example.com").
        
        Returns:
            User: The first user matching the filters.
        
        Raises:
            InvalidRequestError: If any of the filter keys are invalid.
            NoResultFound: If no user matches the filters.
        """
        fields, values = [], []  # Initialize filter fields and values.
        for key, value in kwargs.items():
            if hasattr(User, key):  # Check if filter key exists as an attribute of User.
                fields.append(getattr(User, key))  # Add attribute reference.
                values.append(value)  # Add value.
            else:
                raise InvalidRequestError()  # Raise error for invalid key.
        
        result = self._session.query(User).filter(  # Query the database.
            tuple_(*fields).in_([tuple(values)])
        ).first()
        if result is None:
            raise NoResultFound()  # Raise error if no result is found.
        return result

    def update_user(self, user_id: int, **kwargs) -> None:
        """Updates a user based on a given ID.
        
        Args:
            user_id (int): The ID of the user to update.
            **kwargs: Fields and values to update (e.g., email="new_email@example.com").
        
        Raises:
            ValueError: If any update key is invalid.
        """
        user = self.find_user_by(id=user_id)  # Find user by ID.
        if user is None:
            return
        
        update_source = {}  # Dictionary for updates.
        for key, value in kwargs.items():
            if hasattr(User, key):  # Validate key.
                update_source[getattr(User, key)] = value  # Prepare update dictionary.
            else:
                raise ValueError()  # Raise error for invalid key.

        self._session.query(User).filter(User.id == user_id).update(  # Update user.
            update_source,
            synchronize_session=False,  # Disable session synchronization for performance.
        )
        self._session.commit()  # Commit the updates.