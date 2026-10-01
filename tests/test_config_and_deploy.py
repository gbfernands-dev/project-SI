import asyncio
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from fastapi import HTTPException, UploadFile

from app.config import Settings
from app.services import save_product_image


def production_environment(**overrides):
    environment = {
        "APP_ENV": "production",
        "DATABASE_URL": "postgresql://postgres:password@db.example.supabase.co:5432/postgres",
        "PUBLIC_BASE_URL": "https://loja.example.onrender.com",
        "MP_ACCESS_TOKEN": "TEST-token",
        "MP_WEBHOOK_SECRET": "webhook-secret",
        "SUPABASE_URL": "https://project.supabase.co",
        "SUPABASE_SERVICE_KEY": "service-key",
    }
    environment.update(overrides)
    return environment


def test_production_settings_normalize_postgresql_driver_and_ssl():
    settings = Settings(production_environment())

    assert settings.database_url.startswith("postgresql+psycopg://")
    assert "sslmode=require" in settings.database_url
    assert settings.is_production


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"APP_ENV": "unknown"}, "APP_ENV"),
        ({"DATABASE_URL": "sqlite:///./invalid.db"}, "PostgreSQL"),
        ({"PUBLIC_BASE_URL": "http://localhost:8000"}, "HTTPS"),
        ({"MP_ACCESS_TOKEN": ""}, "MP_ACCESS_TOKEN"),
        ({"SUPABASE_SERVICE_KEY": ""}, "SUPABASE_SERVICE_KEY"),
    ],
)
def test_production_settings_reject_incomplete_environment(overrides, message):
    with pytest.raises(RuntimeError, match=message):
        Settings(production_environment(**overrides))


def test_render_runs_migrations_and_declares_external_configuration():
    render = yaml.safe_load(Path("render.yaml").read_text(encoding="utf-8"))
    service = render["services"][0]
    variables = {item["key"]: item for item in service["envVars"]}

    assert service["name"] == "project-SI"
    assert service["autoDeployTrigger"] == "checksPass"
    assert service["startCommand"].startswith("alembic upgrade head && python -m app.bootstrap &&")
    assert variables["APP_ENV"]["value"] == "production"
    assert variables["PYTHON_VERSION"]["value"] == "3.12.15"
    for name in (
        "DATABASE_URL",
        "MP_ACCESS_TOKEN",
        "MP_WEBHOOK_SECRET",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
        "ADMIN_EMAIL",
        "ADMIN_PASSWORD",
    ):
        assert variables[name]["sync"] is False


def test_schema_creation_is_owned_by_explicit_alembic_migration():
    migration = Path("migrations/versions/20260921_0001_initial_schema.py").read_text(encoding="utf-8")
    startup = Path("app/main.py").read_text(encoding="utf-8")
    bootstrap = Path("app/bootstrap.py").read_text(encoding="utf-8")

    assert "Base.metadata" not in migration
    assert "app.models" not in migration
    assert "Base.metadata.create_all" not in startup
    assert "Base.metadata.create_all" not in bootstrap
    assert migration.count("op.create_table") == 9


def test_production_upload_does_not_fall_back_to_local_disk(monkeypatch):
    settings = SimpleNamespace(
        is_production=True,
        supabase_url="",
        supabase_service_key="",
        static_dir=Path("static"),
    )
    monkeypatch.setattr("app.services.get_settings", lambda: settings)
    upload = UploadFile(filename="produto.png", file=BytesIO(b"image"), headers={"content-type": "image/png"})

    with pytest.raises(HTTPException) as error:
        asyncio.run(save_product_image(upload))

    assert error.value.status_code == 503
