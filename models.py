"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Model for user registration"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")


class UserLogin(BaseModel):
    """Model for user login"""
    username: str
    password: str


class User(BaseModel):
    """Model for user response (no password)"""
    username: str
    email: str
    created_at: datetime


class Token(BaseModel):
    """Model for token response"""
    access_token: str
    token_type: str = "bearer"


class TaskCreate(BaseModel):
    """Model for creating a task"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: str = Field("medium", pattern="^(low|medium|high)$", description="Priority: low, medium, or high")
    completed: bool = Field(False, description="Task completion status")


class TaskUpdate(BaseModel):
    """Model for updating a task (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    completed: Optional[bool] = None


class Task(BaseModel):
    """Model for task response"""
    id: int
    title: str
    description: Optional[str]
    priority: str
    completed: bool
    owner: str
    created_at: datetime
    updated_at: datetime


class Message(BaseModel):
    """Generic message response"""
    message: str
