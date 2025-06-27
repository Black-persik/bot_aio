from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal


class UserIn(BaseModel):
    id: int = Field(default=None, alias="_id")
    name: str = Field(min_length=1, max_length=50)

    model_config = ConfigDict(extra="forbid")


class UserDB(UserIn):
    gender: Optional[Literal["male", "female"]] = None
    language: Optional[Literal["ru", "en"]] = None
    recommendation_method: Optional[Literal["fixed", "kb", "cf"]] = None
    launch_count: int = 0
    current_bundle_version: Optional[int] = None
    bundle_version_at_install: Optional[int] = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class UserOut(UserDB):
    pass


# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_pydantic_core_schema__(cls, _source_type, _handler: GetJsonSchemaHandler) -> core_schema.CoreSchema:
#         return core_schema.no_info_plain_validator_function(cls.validate)

#     @classmethod
#     def validate(cls, v: Any) -> ObjectId:
#         if isinstance(v, ObjectId):
#             return v
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid ObjectId")
#         return ObjectId(v)

#     @classmethod
#     def __get_pydantic_json_schema__(cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> dict:
#         return {
#             "type": "string",
#             "format": "objectid",

# for using objectid as main id
# class UserDB(UserIn):
#     id: PyObjectId = Field(default=None, alias="_id")
#     conversations: List[Conversation] = Field(default_factory=list)

#     model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


# class UserOut(UserIn):
#     id: str = Field(alias="_id")
#     conversations: List[Conversation] = Field(default_factory=list)

#     model_config = ConfigDict(populate_by_name=True)
