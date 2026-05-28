import os
from typing import List

def load_dotenv(dot_env_path: str = ".env"):
    """
    Lightweight, zero-dependency environment variables loader.
    Populates os.environ from a local .env file if it exists.
    """
    if os.path.exists(dot_env_path):
        with open(dot_env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = val

load_dotenv()

class Settings:
    SOLIS_DISABLE_AUTH: bool = os.environ.get("SOLIS_DISABLE_AUTH", "false").lower() == "true"
    SOLIS_API_ID: str = os.environ.get("SOLIS_API_ID", "1300386381676644416")
    SOLIS_API_SECRET: str = os.environ.get("SOLIS_API_SECRET", "mock_secret_key_12345")
    
    SOLIS_API_ID_2: str = os.environ.get("SOLIS_API_ID_2", "1400386381676644416")
    SOLIS_API_SECRET_2: str = os.environ.get("SOLIS_API_SECRET_2", "mock_secret_key_67890")
    
    ALLOWED_HOSTS: List[str] = os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost,127.0.0.1:8000,localhost:8000").split(",")
    CORS_ORIGINS: List[str] = os.environ.get("CORS_ORIGINS", "*").split(",")
    
    RATE_LIMIT_INVERTER: int = int(os.environ.get("RATE_LIMIT_INVERTER", "2"))
    RATE_LIMIT_OTHER: int = int(os.environ.get("RATE_LIMIT_OTHER", "10"))

    def __repr__(self) -> str:
        def mask(s: str) -> str:
            if not s:
                return ""
            if len(s) <= 6:
                return "*" * len(s)
            return s[:3] + "*" * (len(s) - 6) + s[-3:]

        return (
            f"Settings(\n"
            f"  SOLIS_DISABLE_AUTH={self.SOLIS_DISABLE_AUTH},\n"
            f"  SOLIS_API_ID={mask(self.SOLIS_API_ID)},\n"
            f"  SOLIS_API_SECRET={mask(self.SOLIS_API_SECRET)},\n"
            f"  SOLIS_API_ID_2={mask(self.SOLIS_API_ID_2)},\n"
            f"  SOLIS_API_SECRET_2={mask(self.SOLIS_API_SECRET_2)},\n"
            f"  ALLOWED_HOSTS={self.ALLOWED_HOSTS},\n"
            f"  CORS_ORIGINS={self.CORS_ORIGINS},\n"
            f"  RATE_LIMIT_INVERTER={self.RATE_LIMIT_INVERTER},\n"
            f"  RATE_LIMIT_OTHER={self.RATE_LIMIT_OTHER}\n"
            f")"
        )

settings = Settings()
