from uuid import uuid4
from .auth import Auth
from models.user import User  # Assuming User model exists and has a 'get' method to retrieve users from DB

class SessionAuth(Auth):
    """SessionAuth class for session-based authentication."""
    
    # Class attribute to store user IDs by session ID
    user_id_by_session_id = {}

    def create_session(self, user_id: str = None) -> str:
        """Creates a Session ID for a given user_id."""
        if user_id is None or not isinstance(user_id, str):
            return None

        # Generate a new session ID
        session_id = str(uuid4())

        # Store the session ID with the user ID
        self.user_id_by_session_id[session_id] = user_id

        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """Returns a User ID based on a Session ID."""
        if session_id is None or not isinstance(session_id, str):
            return None

        # Retrieve the user ID using the session ID
        return self.user_id_by_session_id.get(session_id)

    def current_user(self, request=None):
        """Overloaded method to return the User instance based on session ID in the cookie."""
        if request is None:
            return None

        # Retrieve the session ID from the request's cookie
        session_id = self.session_cookie(request)

        # Retrieve the user ID associated with the session ID
        user_id = self.user_id_for_session_id(session_id)

        # If user ID is found, return the User instance from the database
        if user_id is not None:
            return User.get(user_id)  # Assuming User.get() method retrieves the user based on ID

        return None
