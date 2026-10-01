from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
import os


ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings:
    static_dir = ROOT_DIR / "static"
    logo_path = static_dir / "assets" / "images" / "logo-atletica.png"

    def __init__(self, environment: Mapping[str, str] | None = None) -> None:
        values = os.environ if environment is None else environment
        self.app_env = values.get("APP_ENV", "development").lower()
        if self.app_env not in {"development", "test", "production"}:
            raise RuntimeError("APP_ENV deve ser development, test ou production.")

        self.database_url = self._normalize_database_url(values.get("DATABASE_URL", "sqlite:///./godzilla.db"))
        self.public_base_url = values.get(
            "PUBLIC_BASE_URL",
            values.get("RENDER_EXTERNAL_URL", "http://localhost:8000"),
        ).rstrip("/")
        self.mp_access_token = values.get("MP_ACCESS_TOKEN", "")
        self.mp_webhook_secret = values.get("MP_WEBHOOK_SECRET", "")
        self.supabase_url = values.get("SUPABASE_URL", "").rstrip("/")
        self.supabase_service_key = values.get("SUPABASE_SERVICE_KEY", "")
        self._validate()

    @staticmethod
    def _normalize_database_url(url: str) -> str:
        if url.startswith("postgres://"):
            url = f"postgresql+psycopg://{url.removeprefix('postgres://')}"
        elif url.startswith("postgresql://"):
            url = f"postgresql+psycopg://{url.removeprefix('postgresql://')}"
        if url.startswith("postgresql+psycopg://") and "sslmode=" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}sslmode=require"
        return url

    def _validate(self) -> None:
        if not self.is_production:
            return
        if not self.database_url.startswith("postgresql+psycopg://"):
            raise RuntimeError("DATABASE_URL de produção deve usar PostgreSQL.")
        if not self.public_base_url.startswith("https://"):
            raise RuntimeError("PUBLIC_BASE_URL de produção deve usar HTTPS.")
        required = {
            "MP_ACCESS_TOKEN": self.mp_access_token,
            "MP_WEBHOOK_SECRET": self.mp_webhook_secret,
            "SUPABASE_URL": self.supabase_url,
            "SUPABASE_SERVICE_KEY": self.supabase_service_key,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(f"Configuração de produção ausente: {', '.join(missing)}.")
        if not self.supabase_url.startswith("https://"):
            raise RuntimeError("SUPABASE_URL de produção deve usar HTTPS.")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
