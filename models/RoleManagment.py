from enum import Enum
from typing import List
from pydantic import BaseModel


class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"
    helper = "helper"
class Role(BaseModel):
    role_name: RoleEnum
    permissions: List[str]  # List of permissions associated with the role