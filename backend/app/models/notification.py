from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId

NotificationType = Literal["answer", "comment", "mention", "vote"]

class NotificationBase(BaseModel):
    recipient_id: PyObjectId
    type: NotificationType
    title: str
    message: str
    related_question_id: Optional[PyObjectId] = None
    related_answer_id: Optional[PyObjectId] = None
    sender_username: Optional[str] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationInDB(NotificationBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Notification(NotificationBase):
    id: str
    is_read: bool
    created_at: datetime

    class Config:
        json_encoders = {ObjectId: str} 