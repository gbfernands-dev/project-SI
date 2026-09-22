from functools import lru_cache
from pathlib import Path
import os


ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings:
    app_env = os.getenv("APP_ENV", "development")
    database_url = os.getenv("DATABASE_URL", "sqlite:///./godzilla.db")
    secret_key = os.getenv("SECRET_KEY", "unsafe-development-secret-change-me")
    public_base_url = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
    mp_access_token = os.getenv("MP_ACCESS_TOKEN", "")
    mp_webhook_secret = os.getenv("MP_WEBHOOK_SECRET", "")
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
    static_dir = ROOT_DIR / "static"
    logo_path = ROOT_DIR / "Logo_atletica.png"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
