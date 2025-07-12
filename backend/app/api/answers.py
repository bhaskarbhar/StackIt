from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from ..database import get_collection
from ..models.answer import AnswerCreate, Answer, AnswerUpdate
from ..models.question import Question
from ..auth.dependencies import get_current_active_user
from ..models.user import UserInDB
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/answers", tags=["answers"])

@router.post("/", response_model=Answer)
async def create_answer(
    answer_data: AnswerCreate,
    question_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_active_user)
):
    answers_collection = get_collection("answers")
    questions_collection = get_collection("questions")
    
    # Check if question exists
    question = await questions_collection.find_one({"_id": ObjectId(question_id)})
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    answer_dict = answer_data.dict()
    answer_dict["question_id"] = ObjectId(question_id)
    answer_dict["author_id"] = current_user.id
    answer_dict["author_username"] = current_user.username
    answer_dict["_id"] = ObjectId()
    answer_dict["created_at"] = datetime.utcnow()
    answer_dict["updated_at"] = datetime.utcnow()
    
    result = await answers_collection.insert_one(answer_dict)
    answer_dict["id"] = str(result.inserted_id)
    
    # Increment answer count for question
    await questions_collection.update_one(
        {"_id": ObjectId(question_id)},
        {"$inc": {"answers_count": 1}}
    )
    
    return Answer(**answer_dict)

@router.get("/question/{question_id}", response_model=List[Answer])
async def get_answers_for_question(
    question_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    answers_collection = get_collection("answers")
    
    try:
        cursor = answers_collection.find({"question_id": ObjectId(question_id)}).sort("votes", -1).skip(skip).limit(limit)
        answers = await cursor.to_list(length=limit)
        
        return [Answer(**{**a, "id": str(a["_id"])}) for a in answers]
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question ID"
        )

@router.put("/{answer_id}", response_model=Answer)
async def update_answer(
    answer_id: str,
    answer_update: AnswerUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    answers_collection = get_collection("answers")
    
    try:
        answer = await answers_collection.find_one({"_id": ObjectId(answer_id)})
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        
        if str(answer["author_id"]) != str(current_user.id) and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this answer"
            )
        
        update_data = answer_update.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data to update"
            )
        
        update_data["updated_at"] = datetime.utcnow()
        
        await answers_collection.update_one(
            {"_id": ObjectId(answer_id)},
            {"$set": update_data}
        )
        
        updated_answer = await answers_collection.find_one({"_id": ObjectId(answer_id)})
        return Answer(**{**updated_answer, "id": str(updated_answer["_id"])})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid answer ID"
        )

@router.delete("/{answer_id}")
async def delete_answer(
    answer_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
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
        
        if str(answer["author_id"]) != str(current_user.id) and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this answer"
            )
        
        # Decrement answer count for question
        await questions_collection.update_one(
            {"_id": answer["question_id"]},
            {"$inc": {"answers_count": -1}}
        )
        
        # Delete answer
        await answers_collection.delete_one({"_id": ObjectId(answer_id)})
        
        return {"message": "Answer deleted successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid answer ID"
        )

@router.post("/{answer_id}/vote")
async def vote_answer(
    answer_id: str,
    vote_type: str = Query(..., regex="^(upvote|downvote)$"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    answers_collection = get_collection("answers")
    
    try:
        answer = await answers_collection.find_one({"_id": ObjectId(answer_id)})
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        
        # Check if user already voted
        vote_key = f"votes.{str(current_user.id)}"
        existing_vote = answer.get("votes", {}).get(str(current_user.id))
        
        vote_value = 1 if vote_type == "upvote" else -1
        
        if existing_vote == vote_value:
            # Remove vote
            await answers_collection.update_one(
                {"_id": ObjectId(answer_id)},
                {
                    "$unset": {vote_key: ""},
                    "$inc": {"votes": -vote_value}
                }
            )
            return {"message": "Vote removed"}
        else:
            # Update vote
            await answers_collection.update_one(
                {"_id": ObjectId(answer_id)},
                {
                    "$set": {vote_key: vote_value},
                    "$inc": {"votes": vote_value - (existing_vote or 0)}
                }
            )
            return {"message": f"Answer {vote_type}d"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid answer ID"
        )

@router.post("/{answer_id}/accept")
async def accept_answer(
    answer_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
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
        
        question = await questions_collection.find_one({"_id": answer["question_id"]})
        if str(question["author_id"]) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only question author can accept answers"
            )
        
        # Unaccept all other answers for this question
        await answers_collection.update_many(
            {"question_id": answer["question_id"]},
            {"$set": {"is_accepted": False}}
        )
        
        # Accept this answer
        await answers_collection.update_one(
            {"_id": ObjectId(answer_id)},
            {"$set": {"is_accepted": True}}
        )
        
        # Update question status
        await questions_collection.update_one(
            {"_id": answer["question_id"]},
            {"$set": {"is_answered": True}}
        )
        
        return {"message": "Answer accepted successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid answer ID"
        ) 