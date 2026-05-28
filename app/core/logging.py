import logging
import re
from app.core.config import settings

class SensitiveDataFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.secrets = [
            settings.SOLIS_API_SECRET,
            settings.SOLIS_API_SECRET_2
        ]
        self.secrets = [s for s in self.secrets if s and len(s) > 4]

    def filter(self, record):
        msg = str(record.msg)
        for sec in self.secrets:
            if sec in msg:
                masked = sec[:3] + "*" * (len(sec) - 6) + sec[-3:]
                msg = msg.replace(sec, masked)
        
        # Mask signatures in headers like "Authorization: API api_id:signature"
        msg = re.sub(r"(Authorization':\s*'API\s+\w+:)([^']*)", r"\1******", msg)
        msg = re.sub(r"(API\s+\w+:)([a-zA-Z0-9+/=]+)", r"\1******", msg)
        
        record.msg = msg
        return True

def setup_logging():
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s.%(module)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)
    
    return logger

logger = setup_logging()
