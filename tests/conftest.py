import os
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./test_godzilla.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["APP_ENV"] = "development"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def csrf_headers(client: TestClient) -> dict[str, str]:
    session = client.get("/api/v1/auth/me").json()
    return {"X-CSRF-Token": session["csrf_token"]}
