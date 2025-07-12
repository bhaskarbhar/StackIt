from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from ..database import get_collection
from ..models.user import User, UserInDB
from ..models.question import Question
from ..models.answer import Answer
from ..auth.dependencies import get_current_admin_user
from bson import ObjectId

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=List[User])
async def get_all_users(
    current_admin: UserInDB = Depends(get_current_admin_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    users_collection = get_collection("users")
    
    cursor = users_collection.find().sort("created_at", -1).skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    
    return [User(**{**u, "id": str(u["_id"])}) for u in users]

@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: str,
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    users_collection = get_collection("users")
    
    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user["role"] == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot ban admin users"
            )
        
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False}}
        )
        
        return {"message": "User banned successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

@router.post("/users/{user_id}/unban")
async def unban_user(
    user_id: str,
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    users_collection = get_collection("users")
    
    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": True}}
        )
        
        return {"message": "User unbanned successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

@router.delete("/questions/{question_id}")
async def delete_question_admin(
    question_id: str,
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    questions_collection = get_collection("questions")
    answers_collection = get_collection("answers")
    
    try:
        question = await questions_collection.find_one({"_id": ObjectId(question_id)})
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Delete associated answers
        await answers_collection.delete_many({"question_id": ObjectId(question_id)})
        
        # Delete question
        await questions_collection.delete_one({"_id": ObjectId(question_id)})
        
        return {"message": "Question deleted by admin"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question ID"
        )

@router.delete("/answers/{answer_id}")
async def delete_answer_admin(
    answer_id: str,
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    answers_collection = get_collection("answers")
    questions_collection = get_collection("questions")
    
    try:
        answer = await answers_collection.find_one({"_id": ObjectId(answer_id)})
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        
        # Decrement answer count for question
        await questions_collection.update_one(
            {"_id": answer["question_id"]},
            {"$inc": {"answers_count": -1}}
        )
        
        # Delete answer
        await answers_collection.delete_one({"_id": ObjectId(answer_id)})
        
        return {"message": "Answer deleted by admin"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid answer ID"
        )

@router.get("/stats")
async def get_admin_stats(current_admin: UserInDB = Depends(get_current_admin_user)):
    users_collection = get_collection("users")
    questions_collection = get_collection("questions")
    answers_collection = get_collection("answers")
    
    total_users = await users_collection.count_documents({})
    active_users = await users_collection.count_documents({"is_active": True})
    total_questions = await questions_collection.count_documents({})
    total_answers = await answers_collection.count_documents({})
    answered_questions = await questions_collection.count_documents({"is_answered": True})
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "banned_users": total_users - active_users,
        "total_questions": total_questions,
        "total_answers": total_answers,
        "answered_questions": answered_questions,
        "unanswered_questions": total_questions - answered_questions
    } 