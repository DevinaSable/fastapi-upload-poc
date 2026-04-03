import asyncio
import bcrypt
from app.db.session import AsyncSessionLocal
from app.models.db_models import User


async def seed():
    async with AsyncSessionLocal() as db:
        user = User(
            username="devd",
            hashed_password=bcrypt.hashpw(b"secret123", bcrypt.gensalt()).decode(),
        )
        db.add(user)
        await db.commit()
        print("✅ Seeded user: devd / secret123")


if __name__ == "__main__":
    asyncio.run(seed())