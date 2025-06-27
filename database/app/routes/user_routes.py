from fastapi import APIRouter, HTTPException
from app.models.user import UserIn, UserOut, UserDB
from app.db import users_collection
import app.cruds.user_crud as crud

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserOut)
async def create_user(user: UserIn):
    user_db = UserDB(**user.model_dump())
    user_id = await crud.create_user(users_collection, user_db)
    user_doc = await crud.read_user_by_id(users_collection, user_id)

    if not user_doc:
        raise HTTPException(status_code=500, detail="User creation failed")

    return UserOut(**user_doc)


@router.get("/{user_id}", response_model=UserOut)
async def read_user(user_id: int):
    user_doc = await crud.read_user_by_id(users_collection, user_id)
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(**user_doc)


@router.put("/{user_id}", response_model=bool)
async def update_user(user_id: int, user: UserDB):
    success = await crud.update_user_by_id(users_collection, user_id, user)
    if not success:
        raise HTTPException(status_code=404, detail="User not updated")
    return True


@router.delete("/{user_id}", response_model=bool)
async def delete_user(user_id: int):
    success = await crud.delete_user_by_id(users_collection, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return True



# from fastapi import APIRouter, HTTPException
# from app.models.user import User
# from app.db import users_collection

# import app.cruds.user_crud as crud

# router = APIRouter(prefix="/users", tags=["Users"])


# @router.post("/", response_model=User)
# async def create_user(user: User):
#     inserted_id = await crud.create_user(users_collection, user)
#     user_doc = await crud.read_user_by_id(users_collection, inserted_id)
#     if not user:
#         raise HTTPException(status_code=500, detail="User creation failed")
    
#     user_doc["_id"] = str(user_doc["_id"])

#     return User(**user_doc)


# @router.get("/{user_id}", response_model=UserOut)
# async def read_user_by_id(user_id: str):
#     user_doc = await crud.read_user_by_id(users_collection, user_id)
#     if not user_doc:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     user_doc["_id"] = str(user_doc["_id"])

#     return UserOut(**user_doc)


# @router.get("/tg/{tg_id}", response_model=User)
# async def read_user_id(tg_id: int):
#     user_doc = await crud.read_user(users_collection, tg_id)
#     if not user_doc:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     user_doc["_id"] = str(user_doc["_id"])
    
#     return User(**user_doc)


# @router.put("/{user_id}", response_model=bool)
# async def update_user_by_id(user_id: str, user: UserIn):
#     success = await crud.update_user(users_collection, user_id, user)
#     if not success:
#         raise HTTPException(status_code=404, detail="User not updated")
#     return True


# @router.delete("/{user_id}", response_model=bool)
# async def delete_user_by_id(user_id: str):
#     success = await crud.delete_user_by_id(users_collection, user_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="User not found")
#     return True


# @router.delete("/tg/{tg_id}", response_model=bool)
# async def delete_user_by_tg_id(tg_id: int):
#     success = await crud.delete_user_by_tg_id(users_collection, tg_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="User not found")
#     return True


# @router.get("/{user_id}/conversations/{conv_index}", response_model=Conversation)
# async def get_conversation_by_index(user_id: str, conv_index: int):
#     conv = await crud.read_conversation_by_index(users_collection, user_id, conv_index)
#     if not conv:
#         raise HTTPException(status_code=404, detail="Conversation not found")
#     return conv


# @router.get("/{user_id}/messages", response_model=list[Message])
# async def get_all_messages(user_id: str):
#     messages = await crud.read_all_messages(users_collection, user_id)
#     if messages is None:
#         raise HTTPException(status_code=404, detail="User or messages not found")
#     return messages


# @router.post("/{user_id}/conversations", response_model=bool)
# async def add_conversation(user_id: str, conversation: Conversation):
#     success = await crud.insert_conversation(users_collection, user_id, conversation)
#     if not success:
#         raise HTTPException(status_code=404, detail="User not found or conversation not added")
#     return True


# @router.post("/{user_id}/conversations/{conv_index}/messages", response_model=bool)
# async def add_message(user_id: str, conv_index: int, message: Message):
#     success = await crud.insert_message(users_collection, user_id, conv_index, message)
#     if not success:
#         raise HTTPException(status_code=404, detail="User or conversation not found")
#     return True