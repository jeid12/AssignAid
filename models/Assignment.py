from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Assignment(BaseModel):
    title: str
    description: str
    subject: str
    files: Optional[List[str]] = []  # List of file paths or URLs
    created_by: Optional[datetime] = None
    status: str = "pending"  # Default to 'pending'
    due_date: Optional[datetime] = None  # Optional due date