import os

# ── Must be set BEFORE any app imports ────────────────────────────
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-ci-only"
os.environ["ENVIRONMENT"] = "dev"
os.environ["DEBUG"] = "true"
os.environ["TESTING"] = "true"       


import asyncio
import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from app.main import app
from app.db.session import get_db, Base
from app.models.db_models import User  # noqa: F401 — registers models

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Create tables once synchronously at module load ───────────────
async def _create_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(_create_tables())

async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Override DB before client is created ─────────────────────────
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
async def seed_and_cleanup():
    """Seed test user before each test, clean up after."""
    async with TestSessionLocal() as session:
        user = User(
            username="devd",
            hashed_password=bcrypt.hashpw(b"secret123", bcrypt.gensalt()).decode(),
        )
        session.add(user)
        await session.commit()

    yield

    async with TestSessionLocal() as session:
        await session.execute(text("DELETE FROM refresh_tokens"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()


@pytest.fixture
def auth_tokens(client):
    response = client.post("/auth/login", json={
        "username": "devd",
        "password": "secret123"
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()


@pytest.fixture
def access_token(auth_tokens):
    return auth_tokens["access_token"]


@pytest.fixture
def refresh_token(auth_tokens):
    return auth_tokens["refresh_token"]


@pytest.fixture
def auth_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}