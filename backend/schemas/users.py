from typing import List

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    id: int = Field(..., example=1, description="Unique identifier for the user")
    username: str = Field(..., max_length=50, example="admin_user", description="Username of the user")
    roles: List[str] = Field(..., example=["admin", "editor"], description="Roles assigned to the user")
    is_active: bool = Field(..., example=True, description="Whether the user account is active")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="securepassword123",
                          description="User's password for authentication")


class UserOut(UserBase):
    """
    Schema for returning user information in API responses
    Excludes sensitive information like passwords
    """
    pass
