from motor.motor_asyncio import AsyncIOMotorCollection
from app.models.conv import ConversationIn, Message
from bson import ObjectId, errors


async def create_conv(collection: AsyncIOMotorCollection, conv: ConversationIn) -> str:
    result = await collection.insert_one(conv.model_dump(by_alias=True, exclude_unset=True))
    return str(result.inserted_id)


async def create_message(collection: AsyncIOMotorCollection, id: str, message: Message) -> bool:
    try:
        oid = ObjectId(id)
    except errors.InvalidId:
        return False
    result = await collection.update_one(
        {"_id": oid},
        {"$push": {"messages": message.model_dump(by_alias=True, exclude_unset=True)}}
    )
    return result.modified_count > 0


async def read_conv(collection: AsyncIOMotorCollection, id: str) -> dict | None:
    try:
        oid = ObjectId(id)
    except errors.InvalidId:
        return None
    return await collection.find_one({"_id": oid})


async def read_user_conv(collection: AsyncIOMotorCollection, user_id: int) -> list[dict]:
    cursor = collection.find({"user_id": user_id})
    return await cursor.to_list(length=100)


async def update_conv(collection: AsyncIOMotorCollection, id: str, conv: ConversationIn) -> bool:
    try:
        oid = ObjectId(id)
    except errors.InvalidId:
        return False
    result = await collection.replace_one({"_id": oid}, conv.model_dump(by_alias=True, exclude_unset=True))
    return result.modified_count > 0


async def delete_conv(collection: AsyncIOMotorCollection, id: str) -> bool:
    try:
        oid = ObjectId(id)
    except errors.InvalidId:
        return False
    result = await collection.delete_one({"_id": oid})
    return result.deleted_count > 0
