import base64
import hashlib
import hmac
import datetime
from fastapi import Request, Depends
from app.core.config import settings
from app.core.security import CREDENTIALS_DB, parse_date_header
from app.core.exceptions import SolisAuthenticationError
from app.core.logging import logger

async def get_request_body(request: Request) -> bytes:
    if not hasattr(request.state, "body"):
        body = await request.body()
        request.state.body = body
        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}
        request._receive = receive
    return request.state.body

async def verify_solis_signature(request: Request, body_bytes: bytes = Depends(get_request_body)):
    if settings.SOLIS_DISABLE_AUTH:
        request.state.api_id = settings.SOLIS_API_ID
        return {"api_id": settings.SOLIS_API_ID}
    
    if request.method != "POST":
        raise SolisAuthenticationError("All SolisCloud V2.0 API endpoints require the POST method.")

    content_md5_header = request.headers.get("Content-MD5")
    content_type_header = request.headers.get("Content-Type")
    date_header = request.headers.get("Date")
    auth_header = request.headers.get("Authorization")
    
    if not all([content_md5_header, content_type_header, date_header, auth_header]):
        msg = "Missing required SolisCloud headers: Content-MD5, Content-Type, Date, or Authorization."
        logger.warning(f"[AUTH FAILED] {msg} Path={request.url.path}")
        raise SolisAuthenticationError(msg)
        
    if "application/json" not in content_type_header.lower():
        msg = "Content-Type must be application/json;charset=UTF-8."
        logger.warning(f"[AUTH FAILED] {msg} Path={request.url.path}")
        raise SolisAuthenticationError(msg)

    calculated_md5 = base64.b64encode(hashlib.md5(body_bytes).digest()).decode("utf-8")
    if not hmac.compare_digest(calculated_md5, content_md5_header):
        msg = f"Content-MD5 mismatch. Calculated: '{calculated_md5}', Received: '{content_md5_header}'."
        logger.warning(f"[AUTH FAILED] {msg} Path={request.url.path}")
        raise SolisAuthenticationError(msg)

    try:
        request_time = parse_date_header(date_header)
    except Exception as e:
        logger.warning(f"[AUTH FAILED] Date parsing error: {str(e)} Path={request.url.path}")
        raise SolisAuthenticationError(f"Invalid Date format header: {str(e)}")

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    time_skew = abs((now_utc - request_time).total_seconds())
    
    if time_skew > 900:
        msg = f"Request timestamp Date skew too high. Server UTC: {now_utc}, Header Date: {request_time} (skew: {time_skew}s)."
        logger.warning(f"[AUTH FAILED] {msg} Path={request.url.path}")
        raise SolisAuthenticationError(msg)

    if not auth_header.startswith("API "):
        msg = "Authorization header must start with 'API '."
        logger.warning(f"[AUTH FAILED] {msg} Path={request.url.path}")
        raise SolisAuthenticationError(msg)
        
    auth_payload = auth_header[4:]
    if ":" not in auth_payload:
        msg = "Authorization format must be 'API {apiId}:{Sign}'."
        logger.warning(f"[AUTH FAILED] {msg} Path={request.url.path}")
        raise SolisAuthenticationError(msg)
        
    api_id, client_sign = auth_payload.split(":", 1)
    
    api_secret = CREDENTIALS_DB.get(api_id)
    if not api_secret:
        msg = f"Unauthorized credentials: Unknown apiId '{api_id}'."
        logger.warning(f"[AUTH FAILED] {msg} Path={request.url.path}")
        raise SolisAuthenticationError(msg)
        
    path = request.url.path
    string_to_sign = f"POST\n{content_md5_header}\n{content_type_header}\n{date_header}\n{path}"
    
    key = api_secret.encode("utf-8")
    msg_bytes = string_to_sign.encode("utf-8")
    calculated_sign = base64.b64encode(hmac.new(key, msg_bytes, hashlib.sha1).digest()).decode("utf-8")
    
    if not hmac.compare_digest(calculated_sign, client_sign):
        msg = "Authentication Signature mismatch. Access denied."
        logger.warning(f"[AUTH FAILED] {msg} Path={request.url.path}")
        raise SolisAuthenticationError(msg)
        
    request.state.api_id = api_id
    return {"api_id": api_id}
