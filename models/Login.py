from pydantic import BaseModel, Field

# User Login Model
class UserLogin(BaseModel):
    username: str = Field(..., description="Unique username", min_length=3, max_length=30)
    password: str = Field(..., description="User password", min_length=6)