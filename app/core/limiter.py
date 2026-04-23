from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter keyed by client IP.
# In production, key by user ID for per-user limits.
limiter = Limiter(key_func=get_remote_address)
