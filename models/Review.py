from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Review(BaseModel):
    assignment_id: str  # ID of the assignment being reviewed
    user_id: str  # ID of the user giving the review
    rating: int  # Rating out of 5
    comment: Optional[str] = None  # Optional review comment
    created_at: datetime