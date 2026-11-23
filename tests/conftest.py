import pytest

import config
import store
from app import app as flask_app

ADMIN = {"email": "admin@passport.com", "password": "Admin1234!"}


@pytest.fixture(autouse=True)
def reset_store(monkeypatch):
    """Cada test arranca solo con el admin precargado y sin sesiones ni bloqueos."""
    monkeypatch.setattr(config, "BCRYPT_ROUNDS", 4)  # hashing rápido en tests
    admin = {k: v for k, v in store.users.items() if v["role"] == "admin"}
    store.users.clear()
    store.users.update(admin)
    store.sessions.clear()
    store.failed_attempts.clear()
    yield


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


@pytest.fixture
def register(client):
    def _register(email="ana@test.com", password="Segura123"):
        return client.post("/auth/register", json={"email": email, "password": password})
    return _register


@pytest.fixture
def login(client):
    def _login(email="ana@test.com", password="Segura123", method="cookie"):
        return client.post("/auth/login", json={"email": email, "password": password, "authMethod": method})
    return _login


@pytest.fixture
def jwt_header(login):
    def _header(email="ana@test.com", password="Segura123"):
        token = login(email, password, method="jwt").get_json()["token"]
        return {"Authorization": f"Bearer {token}"}
    return _header
