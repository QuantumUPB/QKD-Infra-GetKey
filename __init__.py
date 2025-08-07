from .qkdgkt import qkd_get_key, qkd_get_key_resp, qkd_get_destinations, qkd_get_myself

# Re-export under a simpler name
get_destinations = qkd_get_destinations
get_key = qkd_get_key
get_key_with_id = qkd_get_key_resp
get_myself = qkd_get_myself

__all__ = ["get_key", "get_key_with_id", "get_destinations", "get_myself"]

