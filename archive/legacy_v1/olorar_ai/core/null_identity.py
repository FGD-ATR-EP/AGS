from typing import Dict, Any

def annihilate_identity(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitizes input by removing all traces of entity identity.
    Returns a sterile dictionary containing only vectors and context flags.
    """
    forbidden_keys = {
        'user_id', 'username', 'email', 'ip_address',
        'session_token', 'device_id', 'chat_history'
    }

    # Destructive filtering
    clean_payload = {
        k: v for k, v in payload.items()
        if k not in forbidden_keys
    }

    # Enforce anonymity flag
    clean_payload['origin'] = 'NULL'
    return clean_payload
