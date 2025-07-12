from datetime import datetime
from typing import Optional, List, Literal, Any
from pydantic import BaseModel, EmailStr, Field, GetCoreSchemaHandler
from pydantic_core import core_schema
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,  # validation function
            core_schema.union_schema([
                core_schema.str_schema(),  # accept strings
                core_schema.is_instance_schema(ObjectId),  # accept ObjectId instances
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def validate(cls, value):
        # If value is already an ObjectId, return it
        if isinstance(value, ObjectId):
            return value
        # If value is a string, validate and convert
        if isinstance(value, str):
            if not ObjectId.is_valid(value):
                raise ValueError(f"Invalid ObjectId: {value}")
            return ObjectId(value)
        # For other types, try to convert to string first
        str_value = str(value)
        if not ObjectId.is_valid(str_value):
            raise ValueError(f"Invalid ObjectId: {value}")
        return ObjectId(str_value)

UserRole = Literal["user", "admin"]

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = Field(default="user")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=6)

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    is_active: bool = True
    reputation: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class User(UserBase):
    id: str
    reputation: int
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {ObjectId: str} 