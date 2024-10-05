from datetime import datetime
from pydantic import BaseModel


class Subscription(BaseModel):
    user_id: str  # User ID for whom the subscription is active
    plan: str  # e.g., 'basic', 'premium'
    start_date: datetime
    end_date: datetime
    status: str = "active"  # e.g., 'active', 'cancelled'