from slowapi import Limiter
from slowapi.util import get_remote_address
import os


def _get_key(request):
    """Use a fixed key in tests so rate limit is per-test not per-IP."""
    if os.environ.get("ENVIRONMENT") == "dev" and os.environ.get("TESTING") == "true":
        return "test-user"
    return get_remote_address(request)


limiter = Limiter(key_func=_get_key, enabled=os.environ.get("TESTING") != "true")