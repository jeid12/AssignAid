from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Solution(BaseModel):
    assignment_id: str
    answer_file: Optional[List[str]] = []
    answered_by: str  # helper/admin id
    submitted_on: datetime