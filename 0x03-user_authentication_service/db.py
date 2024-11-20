#!/usr/bin/env python3
"""DB module.
This module contains the DB class for interacting with the SQLite
database, handling user operations such as adding, finding, and
updating users.
"""
from sqlalchemy import create_engine, tuple_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from user import Base, User


class DB:
    """DB class.
    Handles database initialization and CRUD operations for users.
    """

    def __init__(self) -> None:
        """Initialize a new DB instance.
        Sets up the SQLite database and creates the tables.
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)  # Drops all tables
        Base.metadata.create_all(self._engine)  # Creates tables
        self.__session = None  # Initialize session as None

    @property
    def _session(self) -> Session:
        """Memoized session object.
        Creates a session for querying the database if not already created.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)  # Create session
            self.__session = DBSession()  # Initialize session
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Adds a new user to the database.
        Takes email and hashed password as inputs and returns the user object.
        """
        try:
            new_user = User(email=email, hashed_password=hashed_password)
            self._session.add(new_user)  # Add user to session
            self._session.commit()  # Commit changes to DB
        except Exception:
            self._session.rollback()  # Rollback in case of error
            new_user = None  # Set new_user to None if exception occurs
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """Finds a user based on a set of filters.
        Uses keyword arguments to search for user attributes and returns
        the first matching user.
        """
        fields, values = [], []  # Initialize fields and values lists
        for key, value in kwargs.items():
            if hasattr(User, key):  # Check if User model has the attribute
                fields.append(getattr(User, key))  # Add field to list
                values.append(value)  # Add value to list
            else:
                raise InvalidRequestError()  # Raise error if invalid field
        # Query the database for the user matching the filters
        result = self._session.query(User).filter(
            tuple_(*fields).in_([tuple(values)])
        ).first()  # Get first matching result
        if result is None:
            raise NoResultFound()  # Raise exception if no user is found
        return result

    def update_user(self, user_id: int, **kwargs) -> None:
        """Updates a user based on a given id.
        Takes user_id and keyword arguments for the fields to be updated.
        """
        user = self.find_user_by(id=user_id)  # Find user by id
        if user is None:
            return  # Return if user is not found
        update_source = {}  # Initialize dictionary to store updates
        for key, value in kwargs.items():
            if hasattr(User, key):  # Check if field is valid
                update_source[getattr(User, key)] = value  # Add to updates
            else:
                raise ValueError()  # Raise error if invalid field
        # Perform the update in the database
        self._session.query(User).filter(User.id == user_id).update(
            update_source,
            synchronize_session=False,  # Don't synchronize session
        )
        self._session.commit()  # Commit changes to the database
