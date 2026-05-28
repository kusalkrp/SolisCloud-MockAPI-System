import time
import threading
from typing import Dict, Tuple, Any, Optional

class TTLCache:
    def __init__(self, default_ttl: float = 300.0):
        self.default_ttl = default_ttl
        self.cache: Dict[str, Tuple[float, Any]] = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                expiry, val = self.cache[key]
                if time.time() < expiry:
                    return val
                else:
                    del self.cache[key]
            return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        duration = ttl if ttl is not None else self.default_ttl
        with self.lock:
            self.cache[key] = (time.time() + duration, value)

# Shared cache for environmental readings
weather_cache = TTLCache(default_ttl=300.0)
