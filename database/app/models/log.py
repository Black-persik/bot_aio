from pydantic import BaseModel, Field, ConfigDict, GetJsonSchemaHandler
from datetime import datetime
from typing import Optional, Any
from bson import ObjectId
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



class LogIn(BaseModel):
    user_id: int
    activity_id: str
    type: str = Field(min_length=1, max_length=50)
    value: Optional[str] = None
    start_time: datetime
    completion_time: datetime
    build_version: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class LogDB(LogIn):
    id: PyObjectId = Field(default=None, alias="_id")

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class LogOut(LogIn):
    id: str = Field(alias="_id")

    model_config = ConfigDict(populate_by_name=True)
