from motor.motor_asyncio import AsyncIOMotorCollection
from app.models.user import UserIn, UserDB


async def create_user(collection: AsyncIOMotorCollection, user: UserDB) -> int:
    await collection.insert_one(user.model_dump(by_alias=True))
    return user.id


async def read_user_by_id(collection: AsyncIOMotorCollection, id: int) -> dict | None:
    return await collection.find_one({"_id": id})


async def update_user_by_id(collection: AsyncIOMotorCollection, id: int, user: UserDB) -> bool:
    result = await collection.replace_one({"_id": id}, user.model_dump(by_alias=True, exclude_unset=True))
    return result.modified_count > 0


async def delete_user_by_id(collection: AsyncIOMotorCollection, id: int) -> bool:
    result = await collection.delete_one({"_id": id})
    return result.deleted_count > 0


# async def delete_user_by_tg_id(collection: AsyncIOMotorCollection, tg_id: int) -> bool:
#     result = await collection.delete_one({"tg_id": tg_id})
#     return result.deleted_count > 0


# async def read_user_by_id(collection: AsyncIOMotorCollection, user_id: str) -> dict | None:
#     try:
#         oid = ObjectId(user_id)
#     except errors.InvalidId:
#         return None
#     return await collection.find_one({"_id": oid})


# async def insert_conversation(collection: AsyncIOMotorCollection, user_id: str, conversation: Conversation) -> bool:
#     try:
#         oid = ObjectId(user_id)
#     except errors.InvalidId:
#         return False
#     result = await collection.update_one(
#         {"_id": oid},
#         {"$push": {"conversations": conversation.model_dump(by_alias=True, exclude_unset=True)}}
#     )
#     return result.modified_count > 0


# async def insert_message(collection: AsyncIOMotorCollection, user_id: str, conv_index: int, message: Message) -> bool:
#     try:
#         oid = ObjectId(user_id)
#     except errors.InvalidId:
#         return False

#     user = await collection.find_one({"_id": oid}, {"conversations": 1})
#     if not user or conv_index >= len(user.get("conversations", [])):
#         return False
    
#     key = f"conversations.{conv_index}.messages"
#     result = await collection.update_one(
#         {"_id": oid},
#         {"$push": {key: message.model_dump(by_alias=True, exclude_unset=True)}}
#     )
#     return result.modified_count > 0


# async def read_conversation_by_index(collection: AsyncIOMotorCollection, user_id: str, conv_index: int) -> dict | None:
#     try:
#         oid = ObjectId(user_id)
#     except errors.InvalidId:
#         return None
    
#     user = await collection.find_one({"_id": oid}, {"conversations": 1})
#     if not user or "conversations" not in user or conv_index >= len(user["conversations"]):
#         return None
    
#     return user["conversations"][conv_index]


# async def read_all_messages(collection: AsyncIOMotorCollection, user_id: str) -> list[dict] | None:
#     try:
#         oid = ObjectId(user_id)
#     except errors.InvalidId:
#         return None
    
#     user = await collection.find_one({"_id": oid}, {"conversations": 1})
#     if not user or "conversations" not in user:
#         return None
    
#     all_messages = []
#     for conv in user["conversations"]:
#         msgs = conv.get("messages", [])
#         all_messages.extend(msgs)
    
#     return all_messages
