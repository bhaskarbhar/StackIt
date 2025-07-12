from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId

class AnswerBase(BaseModel):
    content: str = Field(..., min_length=10)

class AnswerCreate(AnswerBase):
    pass

class AnswerUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=10)

class AnswerInDB(AnswerBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    question_id: PyObjectId
    author_id: PyObjectId
    author_username: str
    votes: int = 0
    is_accepted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Answer(AnswerBase):
    id: str
    question_id: str
    author_id: str
    author_username: str
    votes: int
    is_accepted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {ObjectId: str} 