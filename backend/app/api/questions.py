from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from ..database import get_collection
from ..models.question import QuestionCreate, Question, QuestionUpdate, QuestionInDB
from ..models.answer import Answer, AnswerCreate
from ..auth.dependencies import get_current_active_user, get_current_user
from ..models.user import UserInDB
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/questions", tags=["questions"])

@router.post("/", response_model=Question)
async def create_question(
    question_data: QuestionCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    questions_collection = get_collection("questions")
    
    question_dict = question_data.dict()
    question_dict["author_id"] = str(current_user.id)  # Convert to string for Question model
    question_dict["author_username"] = current_user.username
    question_dict["votes"] = 0
    question_dict["views"] = 0
    question_dict["answers_count"] = 0
    question_dict["is_answered"] = False
    question_dict["created_at"] = datetime.utcnow()
    question_dict["updated_at"] = datetime.utcnow()
    
    # Create the document for MongoDB (with ObjectId)
    mongo_doc = question_dict.copy()
    mongo_doc["_id"] = ObjectId()
    mongo_doc["author_id"] = current_user.id  # Keep as ObjectId for MongoDB
    
    result = await questions_collection.insert_one(mongo_doc)
    question_dict["id"] = str(result.inserted_id)
    
    return Question(**question_dict)

@router.get("/", response_model=List[Question])
async def get_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|votes|views|answers_count)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    questions_collection = get_collection("questions")
    
    # Build filter
    filter_query = {}
    if search:
        filter_query["$text"] = {"$search": search}
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        filter_query["tags"] = {"$in": tag_list}
    
    # Build sort
    sort_direction = -1 if sort_order == "desc" else 1
    sort_query = [(sort_by, sort_direction)]
    
    cursor = questions_collection.find(filter_query).sort(sort_query).skip(skip).limit(limit)
    questions = await cursor.to_list(length=limit)
    
    return [Question(**{**q, "id": str(q["_id"]), "author_id": str(q["author_id"])}) for q in questions if q]

@router.get("/{question_id}", response_model=Question)
async def get_question(question_id: str):
    questions_collection = get_collection("questions")
    
    try:
        question = await questions_collection.find_one({"_id": ObjectId(question_id)})
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Increment view count
        await questions_collection.update_one(
            {"_id": ObjectId(question_id)},
            {"$inc": {"views": 1}}
        )
        
        return Question(**{**question, "id": str(question["_id"]), "author_id": str(question["author_id"])})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question ID"
        )

@router.put("/{question_id}", response_model=Question)
async def update_question(
    question_id: str,
    question_update: QuestionUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    questions_collection = get_collection("questions")
    
    try:
        question = await questions_collection.find_one({"_id": ObjectId(question_id)})
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        if str(question["author_id"]) != str(current_user.id) and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this question"
            )
        
        update_data = question_update.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data to update"
            )
        
        update_data["updated_at"] = datetime.utcnow()
        
        await questions_collection.update_one(
            {"_id": ObjectId(question_id)},
            {"$set": update_data}
        )
        
        updated_question = await questions_collection.find_one({"_id": ObjectId(question_id)})
        if not updated_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found after update"
            )
        return Question(**{**updated_question, "id": str(updated_question["_id"]), "author_id": str(updated_question["author_id"])})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question ID"
        )

@router.delete("/{question_id}")
async def delete_question(
    question_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
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
        
        if str(question["author_id"]) != str(current_user.id) and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this question"
            )
        
        # Delete associated answers
        await answers_collection.delete_many({"question_id": ObjectId(question_id)})
        
        # Delete question
        await questions_collection.delete_one({"_id": ObjectId(question_id)})
        
        return {"message": "Question deleted successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question ID"
        )

@router.post("/{question_id}/vote")
async def vote_question(
    question_id: str,
    vote_type: str = Query(..., regex="^(upvote|downvote)$"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    questions_collection = get_collection("questions")
    
    try:
        question = await questions_collection.find_one({"_id": ObjectId(question_id)})
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Check if user already voted
        vote_key = f"votes.{str(current_user.id)}"
        existing_vote = question.get("votes", {}).get(str(current_user.id))
        
        vote_value = 1 if vote_type == "upvote" else -1
        
        if existing_vote == vote_value:
            # Remove vote
            await questions_collection.update_one(
                {"_id": ObjectId(question_id)},
                {
                    "$unset": {vote_key: ""},
                    "$inc": {"votes": -vote_value}
                }
            )
            return {"message": "Vote removed"}
        else:
            # Update vote
            await questions_collection.update_one(
                {"_id": ObjectId(question_id)},
                {
                    "$set": {vote_key: vote_value},
                    "$inc": {"votes": vote_value - (existing_vote or 0)}
                }
            )
            return {"message": f"Question {vote_type}d"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question ID"
        ) 