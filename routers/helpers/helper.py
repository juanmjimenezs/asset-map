"""General helper"""

from bson import ObjectId
from fastapi import HTTPException, status

def check_id(user_id: str):
    """Check if an Id is not a valid Id for ObjectId"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The ID does not exist.")
