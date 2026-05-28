import time
import threading
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import SolisRateLimitError

class TokenBucket:
    def __init__(self, rate: float, capacity: float):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = threading.Lock()

    def consume(self, amount: float = 1.0) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.last_update = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            if self.tokens >= amount:
                self.tokens -= amount
                return True
            return False

class RateLimiter:
    def __init__(self):
        self.buckets = {}
        self.lock = threading.Lock()

    def get_bucket(self, identifier: str, bucket_type: str, rate: float, capacity: float) -> TokenBucket:
        with self.lock:
            key = (identifier, bucket_type)
            if key not in self.buckets:
                self.buckets[key] = TokenBucket(rate, capacity)
            return self.buckets[key]

rate_limiter = RateLimiter()

class SolisRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.url.path.startswith("/v1/api/"):
            auth_header = request.headers.get("Authorization")
            identifier = None
            if auth_header and auth_header.startswith("API "):
                auth_payload = auth_header[4:]
                if ":" in auth_payload:
                    identifier, _ = auth_payload.split(":", 1)
            
            if not identifier:
                identifier = request.client.host if request.client else "unknown"

            path = request.url.path
            is_inverter = "inverter" in path.lower() or "alarm" in path.lower()
            
            if is_inverter:
                bucket_type = "inverter"
                rate = settings.RATE_LIMIT_INVERTER
                capacity = settings.RATE_LIMIT_INVERTER
            else:
                bucket_type = "other"
                rate = settings.RATE_LIMIT_OTHER
                capacity = settings.RATE_LIMIT_OTHER

            bucket = rate_limiter.get_bucket(identifier, bucket_type, rate, capacity)
            if not bucket.consume(1.0):
                msg = f"Too Many Requests. Rate limit exceeded for {bucket_type} endpoints ({rate} req/sec)."
                logger.warning(f"[RATE LIMIT] Triggered on {path} for identifier: {identifier}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "code": "429",
                        "msg": msg,
                        "data": None
                    }
                )

        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
