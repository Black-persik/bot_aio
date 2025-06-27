import os
from motor.motor_asyncio import AsyncIOMotorClient


MONGO_KEY = os.getenv("MONGO_KEY")


if not MONGO_KEY:
    raise ValueError("MONGODB_URI not set")


client = AsyncIOMotorClient(MONGO_KEY)
db = client.swp_db

users_collection = db.users_new
logs_collection = db.logs_new
conversations_collection = db.conversations