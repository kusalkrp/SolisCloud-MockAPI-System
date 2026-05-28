from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.middleware import SolisRateLimitMiddleware, SecurityHeadersMiddleware
from app.core.exceptions import SolisError
from app.core.logging import logger
from app.api.endpoints import diagnostics, inverters, collectors, epms, weather, stations

app = FastAPI(
    title="Production-Grade SolisCloud Platform API System",
    description="Secure, high-performance modular simulation of Ginlong (Solis) Technologies SolisCloud Platform API V2.0.",
    version="2.0"
)

# --- Global Exception Handlers for Unified API Contract ---

@app.exception_handler(SolisError)
async def solis_exception_handler(request: Request, exc: SolisError):
    # Log business errors beautifully
    if exc.http_status_code == status.HTTP_403_FORBIDDEN:
        logger.warning(f"[SECURITY ALERT] Tenancy (IDOR) violation on {request.url.path}: {exc.msg}")
    elif exc.http_status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        logger.warning(f"[RATE LIMIT] Limit reached on {request.url.path}: {exc.msg}")
    else:
        logger.warning(f"Business Error: Code={exc.code}, Msg={exc.msg}, Path={request.url.path}")
        
    return JSONResponse(
        status_code=exc.http_status_code,
        content={
            "success": False,
            "code": exc.code,
            "msg": exc.msg,
            "data": None
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    detail_msg = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in errors])
    logger.warning(f"Validation Error: Msg={detail_msg}, Path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "code": "422",
            "msg": f"Parameters validation error: {detail_msg}",
            "data": None
        }
    )

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP Exception: Code={exc.status_code}, Msg={exc.detail}, Path={request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": str(exc.status_code),
            "msg": exc.detail,
            "data": None
        }
    )

# --- Standard secure middlewares ---
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# --- Custom secure middlewares ---
app.add_middleware(SolisRateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# --- Include sub-routers ---
app.include_router(diagnostics.router)
app.include_router(inverters.router, prefix="/v1/api")
app.include_router(collectors.router, prefix="/v1/api")
app.include_router(epms.router, prefix="/v1/api")
app.include_router(weather.router, prefix="/v1/api")
app.include_router(stations.router, prefix="/v1/api")
