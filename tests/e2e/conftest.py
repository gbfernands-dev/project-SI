import os
import socket
import subprocess
import time
from pathlib import Path
from uuid import uuid4

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture()
def page():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        yield page
        browser.close()


@pytest.fixture(scope="session")
def live_server():
    port = 8765
    environment = os.environ.copy()
    database_path = Path(f"e2e_godzilla_{uuid4().hex}.db")
    environment["DATABASE_URL"] = f"sqlite+pysqlite:///./{database_path.name}"
    process = subprocess.Popen(["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)], env=environment)
    for _ in range(50):
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                break
        time.sleep(0.2)
    else:
        process.terminate()
        raise RuntimeError("Servidor de E2E não iniciou.")
    yield f"http://127.0.0.1:{port}"
    process.terminate()
    process.wait(timeout=5)
    database_path.unlink(missing_ok=True)
