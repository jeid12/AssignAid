from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from typing import Literal
from enum import Enum

# Role Enum for User, Admin, Helper
class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"
    helper = "helper"


class UserRegistration(BaseModel):
    FullName: str=Field(..., description="Full name of the user")
    username: str = Field(..., description="Unique username", min_length=6, max_length=12)
    email: EmailStr=Field(..., description="Valid email address")
    password: str = Field(..., description="Password with at least 6 characters",min_length=8, max_length=100)
    role: RoleEnum = Field(..., description="Role of the user", example="user")
    gender: Literal['male', 'female', 'other'] = Field(..., description="Gender of the user")



class UserRegistrationResponse(BaseModel):
            id: str
            FullName: str
            username: str
            email: EmailStr
            role: RoleEnum
            gender: Literal['male', 'female', 'other']

           
    