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
    user_votes: dict = Field(default_factory=dict, description="Track individual user votes: {user_id: vote_value}")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

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
    user_votes: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {ObjectId: str} 