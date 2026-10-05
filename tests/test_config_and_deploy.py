import asyncio
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from fastapi import HTTPException, UploadFile

from app.config import Settings
from app.services import create_payment_preference, save_product_image


def production_environment(**overrides):
    environment = {
        "APP_ENV": "production",
        "DATABASE_URL": "postgresql://postgres:password@db.example.supabase.co:5432/postgres",
        "PUBLIC_BASE_URL": "https://loja.example.onrender.com",
        "MP_ACCESS_TOKEN": "TEST-token",
        "MP_PUBLIC_KEY": "TEST-public-key",
        "MP_CLIENT_ID": "123456789",
        "MP_CLIENT_SECRET": "client-secret",
        "MP_WEBHOOK_SECRET": "webhook-secret",
        "MP_ENVIRONMENT": "test",
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
    assert settings.mp_environment == "test"


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"APP_ENV": "unknown"}, "APP_ENV"),
        ({"DATABASE_URL": "sqlite:///./invalid.db"}, "PostgreSQL"),
        ({"PUBLIC_BASE_URL": "http://localhost:8000"}, "HTTPS"),
        ({"MP_ACCESS_TOKEN": ""}, "MP_ACCESS_TOKEN"),
        ({"MP_PUBLIC_KEY": ""}, "MP_PUBLIC_KEY"),
        ({"MP_CLIENT_ID": ""}, "MP_CLIENT_ID"),
        ({"MP_CLIENT_SECRET": ""}, "MP_CLIENT_SECRET"),
        ({"MP_ENVIRONMENT": "invalid"}, "MP_ENVIRONMENT"),
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
    assert variables["MP_ENVIRONMENT"]["value"] == "production"
    for name in (
        "DATABASE_URL",
        "MP_ACCESS_TOKEN",
        "MP_PUBLIC_KEY",
        "MP_CLIENT_ID",
        "MP_CLIENT_SECRET",
        "MP_WEBHOOK_SECRET",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
        "ADMIN_EMAIL",
        "ADMIN_PASSWORD",
        "ATHLETICS_ADMIN_EMAIL",
        "ATHLETICS_ADMIN_PASSWORD",
    ):
        assert variables[name]["sync"] is False

    assert "provision_admin_accounts(db)" in Path("app/main.py").read_text(encoding="utf-8")


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


@pytest.mark.parametrize(
    ("environment", "expected_url"),
    [
        ("test", "https://sandbox.mercadopago.test/checkout"),
        ("production", "https://mercadopago.test/checkout"),
    ],
)
def test_checkout_url_matches_configured_mercado_pago_environment(monkeypatch, environment, expected_url):
    settings = SimpleNamespace(
        mp_access_token="token",
        mp_environment=environment,
        public_base_url="https://loja.example",
        is_production=True,
    )
    response = SimpleNamespace(
        ok=True,
        json=lambda: {
            "sandbox_init_point": "https://sandbox.mercadopago.test/checkout",
            "init_point": "https://mercadopago.test/checkout",
        },
    )
    monkeypatch.setattr("app.services.get_settings", lambda: settings)
    monkeypatch.setattr("app.services.requests.post", lambda *args, **kwargs: response)

    assert create_payment_preference(1, [{"title": "Produto", "quantity": 1, "unit_price": 0.5}]) == expected_url


def test_frontend_assets_are_versioned_and_product_cards_expose_gallery():
    index = Path("static/index.html").read_text(encoding="utf-8")
    script = Path("static/js/app.js").read_text(encoding="utf-8")
    stylesheet = Path("static/css/main.css").read_text(encoding="utf-8")

    assert '/static/css/main.css?v=' in index
    assert '/static/js/app.js?v=' in index
    assert 'class="card-gallery-thumbnails"' in script
    assert "background: var(--product-image-background)" in stylesheet
    assert 'data-admin-action="edit"' in script
    assert 'data-admin-action="delete"' in script
    assert "Saúde e configurações" in script
    assert "Contas criadas" in script
    assert "border-radius: 50%" in stylesheet
    assert "@media (prefers-reduced-motion: reduce)" in stylesheet
    assert "@media (max-width: 1024px)" in stylesheet
    assert "@media (max-width: 640px)" in stylesheet


def test_mercado_pago_secrets_are_only_declared_as_environment_variables():
    tracked_configuration = "\n".join(
        Path(path).read_text(encoding="utf-8")
        for path in (".env.example", "render.yaml", "README.md", "app/config.py")
    )

    assert "APP_USR-" not in tracked_configuration
    for variable in ("MP_PUBLIC_KEY", "MP_ACCESS_TOKEN", "MP_CLIENT_ID", "MP_CLIENT_SECRET"):
        assert variable in tracked_configuration


def test_admin_scope_migration_is_explicit_and_reversible():
    migration = Path("migrations/versions/20261005_0003_admin_observability.py").read_text(encoding="utf-8")

    assert 'batch_alter_table("users")' in migration
    assert "batch_op.add_column" in migration
    assert "admin_scope" in migration
    assert "registration_ip" in migration
    assert "last_login_ip" in migration
    assert "op.drop_column" in migration
