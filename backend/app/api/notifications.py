from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from ..database import get_collection
from ..models.notification import Notification, NotificationCreate
from ..auth.dependencies import get_current_active_user
from ..models.user import UserInDB
from bson import ObjectId

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[Notification])
async def get_notifications(
    current_user: UserInDB = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False)
):
    notifications_collection = get_collection("notifications")
    
    filter_query = {"recipient_id": current_user.id}
    if unread_only:
        filter_query["is_read"] = False
    
    cursor = notifications_collection.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
    notifications = await cursor.to_list(length=limit)
    
    return [Notification(**{**n, "id": str(n["_id"])}) for n in notifications]

@router.get("/unread-count")
async def get_unread_count(current_user: UserInDB = Depends(get_current_active_user)):
    notifications_collection = get_collection("notifications")
    
    count = await notifications_collection.count_documents({
        "recipient_id": current_user.id,
        "is_read": False
    })
    
    return {"unread_count": count}

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    notifications_collection = get_collection("notifications")
    
    try:
        notification = await notifications_collection.find_one({"_id": ObjectId(notification_id)})
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        if str(notification["recipient_id"]) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to mark this notification as read"
            )
        
        await notifications_collection.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"is_read": True}}
        )
        
        return {"message": "Notification marked as read"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID"
        )

@router.post("/mark-all-read")
async def mark_all_notifications_read(current_user: UserInDB = Depends(get_current_active_user)):
    notifications_collection = get_collection("notifications")
    
    await notifications_collection.update_many(
        {
            "recipient_id": current_user.id,
            "is_read": False
        },
        {"$set": {"is_read": True}}
    )
    
    return {"message": "All notifications marked as read"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    notifications_collection = get_collection("notifications")
    
    try:
        notification = await notifications_collection.find_one({"_id": ObjectId(notification_id)})
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        if str(notification["recipient_id"]) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this notification"
            )
        
        await notifications_collection.delete_one({"_id": ObjectId(notification_id)})
        
        return {"message": "Notification deleted successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID"
        ) 