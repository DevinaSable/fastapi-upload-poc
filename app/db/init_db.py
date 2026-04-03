from app.db.session import engine, Base
from app.models import db_models  # noqa: F401 — registers models with Base


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)