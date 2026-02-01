import json
import os
import time
import logging
from typing import Optional, Dict
from src.backend.genesis_core.models.auth import UserSession, TokenSet, IdentityProfile

logger = logging.getLogger("AuthManager")

class AuthManager:
    """Manages persistent user identities and sessions using a JSON store.

    This class handles the lifecycle of user sessions, including loading from disk,
    caching in memory, updating session details, and saving back to disk.
    """

    def __init__(self, filepath: str = "auth_sessions.json"):
        """Initializes the AuthManager.

        Args:
            filepath: The path to the JSON file used for session persistence.
        """
        self.filepath = filepath
        self._cache: Dict[str, UserSession] = {}
        self._load()

    def _load(self):
        """Loads user sessions from the JSON store into the memory cache.

        Handles missing files gracefully and logs any errors during loading.
        """
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                for uid, user_data in data.items():
                    self._cache[uid] = UserSession(**user_data)
            logger.info(f"Loaded {len(self._cache)} identities from store.")
        except Exception as e:
            logger.error(f"Failed to load auth store: {e}")

    def save(self):
        """Persists the current memory cache of user sessions to the JSON file.

        Logs an error if the file operation fails.
        """
        try:
            data = {uid: session.model_dump(mode='json') for uid, session in self._cache.items()}
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save auth store: {e}")

    def get_user(self, user_id: str) -> Optional[UserSession]:
        """Retrieves a user session by ID.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The UserSession object if found, otherwise None.
        """
        return self._cache.get(user_id)

    def upsert_user(self, user_id: str, identity: IdentityProfile, tokens: TokenSet) -> UserSession:
        """Updates or inserts a user session.

        If the user exists, their identity and tokens are updated.
        If not, a new session is created.
        The storage is immediately saved after the operation.

        Args:
            user_id: The unique identifier of the user.
            identity: The user's profile information.
            tokens: The current set of authentication tokens.

        Returns:
            The updated or newly created UserSession.
        """
        now = time.time()

        if user_id in self._cache:
            # Update existing
            session = self._cache[user_id]
            session.identity = identity # Update profile if changed
            session.tokens = tokens     # Rotate tokens
            session.last_accessed = now
        else:
            # Create new
            session = UserSession(
                user_id=user_id,
                identity=identity,
                tokens=tokens,
                created_at=now,
                last_accessed=now
            )
            self._cache[user_id] = session

        self.save()
        return session
