from pydantic import BaseModel, Field, ConfigDict, GetJsonSchemaHandler
from bson import ObjectId
from typing import Optional, Literal, List, Any
from datetime import datetime
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler: GetJsonSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> dict:
        return {
            "type": "string",
            "format": "objectid",
        }


class Message(BaseModel):
    sender: Literal["user", "bot"]
    text: str = Field(min_length=1)
    time: datetime

    model_config = ConfigDict(extra="forbid")


class ConversationIn(BaseModel):
    user_id: int
    messages: Optional[List[Message]] = []

    model_config = ConfigDict(extra="forbid")


class ConversationDB(ConversationIn):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class ConversationOut(ConversationIn):
    id: str = Field(alias="_id")

    model_config = ConfigDict(populate_by_name=True)
