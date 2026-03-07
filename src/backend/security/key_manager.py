import json
import os
import logging
import uuid
import datetime
from typing import Dict, Optional, List
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger("KeyManager")

class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED" # Payment issue / Paused
    REVOKED = "REVOKED"     # Ban
    PENDING = "PENDING"     # Created but not approved

class KeyTier(str, Enum):
    FREE = "FREE"
    STANDARD = "STANDARD"
    PRO = "PRO"
    INTERNAL = "INTERNAL"

class AccessKeyRecord(BaseModel):
    key_id: str
    access_key: str # The secret token
    abe_id: str # Link to Identity Contract
    tier: KeyTier = KeyTier.FREE
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    created_at: float
    last_used: float = 0.0
    label: Optional[str] = None

class KeyStoreData(BaseModel):
    keys: Dict[str, AccessKeyRecord] = {} # access_key -> Record

class KeyManager:
    """
    Manages Access Keys and Subscription States.
    Uses a simple JSON file as the source of truth.
    """
    def __init__(self, filepath: str = "access_keys.json"):
        self.filepath = filepath
        self.store = KeyStoreData()
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            # Create default internal key if missing?
            self._save()
            return

        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                self.store = KeyStoreData(**data)
        except Exception as e:
            logger.error(f"Failed to load KeyStore: {e}")

    def _save(self):
        try:
            with open(self.filepath, 'w') as f:
                f.write(self.store.model_dump_json(indent=2))
        except Exception as e:
            logger.error(f"Failed to save KeyStore: {e}")

    def validate_access(self, access_key: str, abe_id: str) -> bool:
        """
        Core Check:
        1. Key exists?
        2. Key matches .abe Identity?
        3. Subscription is ACTIVE?
        """
        if access_key not in self.store.keys:
            logger.warning(f"Access Denied: Key not found")
            return False

        record = self.store.keys[access_key]

        # Identity Bind Check
        if record.abe_id != abe_id:
            logger.warning(f"Access Denied: Key bound to {record.abe_id}, tried {abe_id}")
            return False

        # Subscription Check
        if record.status != SubscriptionStatus.ACTIVE and record.tier != KeyTier.INTERNAL:
            logger.warning(f"Access Denied: Subscription status is {record.status}")
            return False

        # Update Usage
        record.last_used = datetime.datetime.now().timestamp()
        self._save() # Naive persist on use (optimize later)

        return True

    def create_key(self, abe_id: str, tier: KeyTier = KeyTier.FREE, label: str = "") -> str:
        """Generates a new Access Key for an Identity."""
        new_key = f"ak-{uuid.uuid4().hex}"
        record = AccessKeyRecord(
            key_id=uuid.uuid4().hex,
            access_key=new_key,
            abe_id=abe_id,
            tier=tier,
            status=SubscriptionStatus.PENDING if tier != KeyTier.INTERNAL else SubscriptionStatus.ACTIVE,
            created_at=datetime.datetime.now().timestamp(),
            label=label
        )
        self.store.keys[new_key] = record
        self._save()
        logger.info(f"Generated Key for {abe_id} [{tier}]")
        return new_key

    def set_status(self, access_key: str, status: SubscriptionStatus):
        """Admin Control: Change subscription status."""
        if access_key in self.store.keys:
            self.store.keys[access_key].status = status
            self._save()
            logger.info(f"Updated status for key ...{access_key[-4:]} to {status}")

    def get_all_keys(self) -> List[AccessKeyRecord]:
        return list(self.store.keys.values())

    def get_record(self, access_key: str) -> Optional[AccessKeyRecord]:
        return self.store.keys.get(access_key)
