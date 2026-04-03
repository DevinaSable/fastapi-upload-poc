import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import bcrypt

from app.main import app
from app.db.session import get_db, Base
from app.models.db_models import User

# ── In-memory SQLite for tests (no PostgreSQL needed in CI) ────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Create all tables once for the test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def seed_user():
    """Insert test user before each test, clean up after."""
    async with TestSessionLocal() as session:
        user = User(
            username="devd",
            hashed_password=bcrypt.hashpw(b"secret123", bcrypt.gensalt()).decode(),
        )
        session.add(user)
        await session.commit()
    yield
    # Cleanup after each test
    async with TestSessionLocal() as session:
        from sqlalchemy import text
        await session.execute(text("DELETE FROM refresh_tokens"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_tokens(client):
    """Login and return both tokens."""
    response = client.post("/auth/login", json={
        "username": "devd",
        "password": "secret123"
    })
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