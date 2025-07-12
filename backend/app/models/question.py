from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId

class QuestionBase(BaseModel):
    title: str = Field(..., min_length=10, max_length=300)
    description: str = Field(..., min_length=20)
    tags: List[str] = Field(..., description="List of tags (1-5 tags)")

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=10, max_length=300)
    description: Optional[str] = Field(None, min_length=20)
    tags: Optional[List[str]] = Field(None, description="List of tags (1-5 tags)")

class QuestionInDB(QuestionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    author_id: PyObjectId
    author_username: str
    votes: int = 0
    views: int = 0
    answers_count: int = 0
    is_answered: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Question(QuestionBase):
    id: str
    author_id: str
    author_username: str
    votes: int
    views: int
    answers_count: int
    is_answered: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {ObjectId: str} 