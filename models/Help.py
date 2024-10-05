from datetime import datetime
from pydantic import BaseModel


class HelpRequest(BaseModel):
    assignment_id: str  # ID of the assignment needing help
    requested_by: str  # User ID of the requester
    status: str = "pending"  # e.g., 'pending', 'in-progress', 'completed'
    created_at: datetime
