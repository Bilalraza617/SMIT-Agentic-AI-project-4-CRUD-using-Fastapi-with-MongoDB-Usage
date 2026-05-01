from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database

async def get_db() -> AsyncIOMotorDatabase:
    db = get_database()
    yield db
