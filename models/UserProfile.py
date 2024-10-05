from pydantic import BaseModel, Optional, List
class UserProfile(BaseModel):
    user_id: str  # User ID linked to the registration
    bio: Optional[str] = None
    profile_picture: Optional[str] = None  # URL to profile picture
    skills: Optional[List[str]] = []  # List of skills or subjects of expertise