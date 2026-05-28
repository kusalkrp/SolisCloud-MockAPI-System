from fastapi import status

class SolisError(Exception):
    def __init__(self, http_status_code: int, code: str, msg: str):
        super().__init__(msg)
        self.http_status_code = http_status_code
        self.code = code
        self.msg = msg

class SolisAuthenticationError(SolisError):
    def __init__(self, msg: str = "Authentication failed. Access denied."):
        super().__init__(
            http_status_code=status.HTTP_401_UNAUTHORIZED,
            code="401",
            msg=msg
        )

class SolisTenancyError(SolisError):
    def __init__(self, msg: str = "Access Denied: Resource ownership check failed."):
        super().__init__(
            http_status_code=status.HTTP_403_FORBIDDEN,
            code="403",
            msg=msg
        )

class SolisRateLimitError(SolisError):
    def __init__(self, msg: str = "Too Many Requests. Rate limit exceeded."):
        super().__init__(
            http_status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="429",
            msg=msg
        )

class SolisValidationError(SolisError):
    def __init__(self, msg: str = "Parameters validation error."):
        super().__init__(
            http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="422",
            msg=msg
        )
