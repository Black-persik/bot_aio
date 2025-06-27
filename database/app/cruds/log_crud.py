from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from app.models.log import LogIn


async def create_log(collection: AsyncIOMotorCollection, log: LogIn):
    result = await collection.insert_one(log.model_dump(by_alias=True, exclude_unset=True))
    return str(result.inserted_id)


async def read_log(collection: AsyncIOMotorCollection, id: str):
    return await collection.find_one({"_id": ObjectId(id)})


async def update_log(collection: AsyncIOMotorCollection, id: str, log: LogIn):
    result = await collection.replace_one({"_id": ObjectId(id)}, log.model_dump(by_alias=True, exclude_unset=True))
    return result.modified_count


async def delete_log(collection: AsyncIOMotorCollection, id: str):
    result = await collection.delete_one({"_id": ObjectId(id)})
    return result.deleted_count