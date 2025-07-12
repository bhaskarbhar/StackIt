from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from ..database import get_collection
from ..models.answer import AnswerCreate, Answer, AnswerUpdate
from ..models.question import Question
from ..auth.dependencies import get_current_active_user
from ..models.user import UserInDB, PyObjectId
from bson import ObjectId
import datetime
from ..models.notification import NotificationCreate

router = APIRouter(prefix="/answers", tags=["answers"])

@router.post("/", response_model=Answer)
async def create_answer(
    answer_data: AnswerCreate,
    question_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_active_user)
):
    answers_collection = get_collection("answers")
    questions_collection = get_collection("questions")
    notifications_collection = get_collection("notifications")
    
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
    answer_dict["votes"] = 0
    answer_dict["user_votes"] = {}
    answer_dict["_id"] = ObjectId()
    answer_dict["created_at"] = datetime.datetime.now()
    answer_dict["updated_at"] = datetime.datetime.now()
    
    result = await answers_collection.insert_one(answer_dict)
    answer_dict["id"] = str(result.inserted_id)
    
    # Increment answer count for question
    await questions_collection.update_one(
        {"_id": ObjectId(question_id)},
        {"$inc": {"answers_count": 1}}
    )
    
    # Notify question author (if not answering own question)
    if str(question["author_id"]) != str(current_user.id):
        notification = NotificationCreate(
            recipient_id=question["author_id"],
            type="answer",
            title="New Answer to Your Question",
            message=f"{current_user.username} answered your question: {question['title']}",
            related_question_id=PyObjectId(question["_id"]),
            related_answer_id=PyObjectId(answer_dict["_id"]),
            sender_username=current_user.username
        )
        await notifications_collection.insert_one(notification.dict(by_alias=True))
    
    # Before returning, convert ObjectId fields to strings
    answer_dict["id"] = str(answer_dict["_id"])
    answer_dict["question_id"] = str(answer_dict["question_id"])
    answer_dict["author_id"] = str(answer_dict["author_id"])
    return Answer(**answer_dict)

@router.get("/question/{question_id}", response_model=List[Answer])
async def get_answers_for_question(
    question_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    answers_collection = get_collection("answers")
    
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(question_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid question ID format"
            )
        
        cursor = answers_collection.find({"question_id": ObjectId(question_id)}).sort("votes", -1).skip(skip).limit(limit)
        answers = await cursor.to_list(length=limit)
        
        return [Answer(**{
            **a, 
            "id": str(a["_id"]), 
            "question_id": str(a["question_id"]),
            "author_id": str(a["author_id"]),
            "user_votes": a.get("user_votes", {}),
            "votes": a.get("votes", 0),
            "created_at": a.get("created_at", datetime.datetime.now()),
            "updated_at": a.get("updated_at", datetime.datetime.now())
        }) for a in answers]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching answers: {str(e)}"
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
        
        if str(answer["author_id"]) != str(current_user.id):
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
        
        update_data["updated_at"] = datetime.datetime.now()
        
        await answers_collection.update_one(
            {"_id": ObjectId(answer_id)},
            {"$set": update_data}
        )
        
        updated_answer = await answers_collection.find_one({"_id": ObjectId(answer_id)})
        if not updated_answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found after update"
            )
        return Answer(**{
            **updated_answer, 
            "id": str(updated_answer["_id"]), 
            "question_id": str(updated_answer["question_id"]),
            "author_id": str(updated_answer["author_id"]),
            "user_votes": updated_answer.get("user_votes", {}),
            "votes": updated_answer.get("votes", 0),
            "created_at": updated_answer.get("created_at", datetime.datetime.now()),
            "updated_at": updated_answer.get("updated_at", datetime.datetime.now())
        })
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
    notifications_collection = get_collection("notifications")
    
    try:
        answer = await answers_collection.find_one({"_id": ObjectId(answer_id)})
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        
        # Check if user already voted
        user_votes = answer.get("user_votes", {}) if answer else {}
        user_id_str = str(current_user.id)
        existing_vote = user_votes.get(user_id_str, 0)
        
        vote_value = 1 if vote_type == "upvote" else -1
        
        if existing_vote == vote_value:
            # Remove vote - user is clicking the same vote type again
            await answers_collection.update_one(
                {"_id": ObjectId(answer_id)},
                {
                    "$unset": {f"user_votes.{user_id_str}": ""},
                    "$inc": {"votes": -vote_value}
                }
            )
            return {"message": "Vote removed"}
        else:
            # Update vote - either new vote or changing vote type
            vote_diff = vote_value - existing_vote
            await answers_collection.update_one(
                {"_id": ObjectId(answer_id)},
                {
                    "$set": {f"user_votes.{user_id_str}": vote_value},
                    "$inc": {"votes": vote_diff}
                }
            )
            return {"message": f"Answer {vote_type}d"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid answer ID"
        ) 