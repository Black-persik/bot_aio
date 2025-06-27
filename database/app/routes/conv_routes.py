from fastapi import APIRouter, HTTPException
from app.models.conv import ConversationIn, ConversationOut, Message
import app.cruds.conv_crud as crud
from app.db import conversations_collection


router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("/", response_model=ConversationOut)
async def create_conversation(conv: ConversationIn):
    conv_id = await crud.create_conv(conversations_collection, conv)
    conversation = await crud.read_conv(conversations_collection, conv_id)
    if not conversation:
        raise HTTPException(status_code=500, detail="Conversation creation failed")
    
    conversation["_id"] = str(conversation["_id"])
    
    return ConversationOut(**conversation)


@router.post("/{conv_id}/messages", response_model=bool)
async def add_message(conv_id: str, message: Message):
    success = await crud.create_message(conversations_collection, conv_id, message)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found or message not added")
    return True


@router.get("/{conv_id}", response_model=ConversationOut)
async def get_conversation(conv_id: str):
    conversation = await crud.read_conv(conversations_collection, conv_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation["_id"] = str(conversation["_id"])
    return ConversationOut(**conversation)



@router.get("/user/{user_id}", response_model=list[ConversationOut])
async def get_user_conversations(user_id: int):
    conversations = await crud.read_user_conv(conversations_collection, user_id)
    if not conversations:
        raise HTTPException(status_code=404, detail="Conversations not found")
    
    # Преобразуем _id в строку для каждого документа
    for conv in conversations:
        conv["_id"] = str(conv["_id"])
    
    return [ConversationOut(**conv) for conv in conversations]



@router.put("/{conv_id}", response_model=bool)
async def update_conversation(conv_id: str, conv: ConversationIn):
    success = await crud.update_conv(conversations_collection, conv_id, conv)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found or not updated")
    return True


@router.delete("/{conv_id}", response_model=bool)
async def delete_conversation(conv_id: str):
    success = await crud.delete_conv(conversations_collection, conv_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found or not deleted")
    return True