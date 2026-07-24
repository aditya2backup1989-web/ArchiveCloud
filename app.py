"""
Main FastAPI application: Secure Task Management API
"""
from fastapi import FastAPI, Depends, HTTPException, status
from datetime import timedelta
from typing import List

# Import our modules
from models import (
    UserRegister, UserLogin, User, Token, 
    TaskCreate, TaskUpdate, Task, Message
)
from auth import (
    hash_password, verify_password, create_access_token, 
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
import database as db
from security_config import configure_security

# Create FastAPI app
app = FastAPI(
    title="Secure Task Management API",
    description="A secure REST API with JWT authentication for managing tasks",
    version="1.0.0"
)

# Configure security (CORS, headers, middleware)
configure_security(app)


@app.get("/", response_model=Message, tags=["Health"])
async def health_check():
    """
    Health check endpoint - publicly accessible
    """
    return {"message": "Secure Task Management API is running"}


@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register_user(user_data: UserRegister):
    """
    Register a new user
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Password (minimum 6 characters)
    """
    # Check if username already exists
    if db.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if db.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = hash_password(user_data.password)
    
    # Create user in database
    user = db.create_user(user_data.username, user_data.email, hashed_password)
    
    # Return user data (without password)
    return User(
        username=user["username"],
        email=user["email"],
        created_at=user["created_at"]
    )


@app.post("/login", response_model=Token, tags=["Authentication"])
async def login(credentials: UserLogin):
    """
    Login and receive JWT access token
    
    - **username**: Your username
    - **password**: Your password
    
    Returns a JWT token to use in the Authorization header for protected routes
    """
    # Get user from database
    user = db.get_user_by_username(credentials.username)
    
    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=User, tags=["Users"])
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Requires: Valid JWT token in Authorization header
    """
    user = db.get_user_by_username(current_user)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User(
        username=user["username"],
        email=user["email"],
        created_at=user["created_at"]
    )


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(task_data: TaskCreate, current_user: str = Depends(get_current_user)):
    """
    Create a new task (authenticated users only)
    
    - **title**: Task title (required, 1-200 characters)
    - **description**: Task description (optional, max 1000 characters)
    - **priority**: Priority level (low, medium, high)
    - **completed**: Completion status (default: false)
    
    Requires: Valid JWT token in Authorization header
    """
    task = db.create_task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        completed=task_data.completed,
        owner=current_user
    )
    
    return Task(**task)


@app.get("/tasks", response_model=List[Task], tags=["Tasks"])
async def get_tasks(current_user: str = Depends(get_current_user)):
    """
    Get all tasks for the current user
    
    Requires: Valid JWT token in Authorization header
    """
    tasks = db.get_tasks_by_owner(current_user)
    return [Task(**task) for task in tasks]


@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def get_task(task_id: int, current_user: str = Depends(get_current_user)):
    """
    Get a specific task by ID
    
    Users can only access their own tasks
    
    Requires: Valid JWT token in Authorization header
    """
    task = db.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user owns this task (authorization)
    if task["owner"] != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task"
        )
    
    return Task(**task)


@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def update_task(
    task_id: int, 
    task_updates: TaskUpdate, 
    current_user: str = Depends(get_current_user)
):
    """
    Update a task
    
    Users can only update their own tasks. All fields are optional.
    
    - **title**: New task title
    - **description**: New task description
    - **priority**: New priority level
    - **completed**: New completion status
    
    Requires: Valid JWT token in Authorization header
    """
    task = db.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user owns this task (authorization)
    if task["owner"] != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this task"
        )
    
    # Update task
    updates = task_updates.model_dump(exclude_unset=True)
    updated_task = db.update_task(task_id, updates)
    
    return Task(**updated_task)


@app.delete("/tasks/{task_id}", response_model=Message, tags=["Tasks"])
async def delete_task(task_id: int, current_user: str = Depends(get_current_user)):
    """
    Delete a task
    
    Users can only delete their own tasks
    
    Requires: Valid JWT token in Authorization header
    """
    task = db.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user owns this task (authorization)
    if task["owner"] != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this task"
        )
    
    # Delete task
    db.delete_task(task_id)
    
    return {"message": "Task deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
