from pydantic import BaseModel

from datetime import datetime

class Notification(BaseModel):
    user_id: str  # User receiving the notification
    message: str
    created_at: datetime
    is_read: bool = False  # Flag to indicate if the notification has been read