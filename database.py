"""
In-memory database for demonstration purposes
In production, use a real database like PostgreSQL or MongoDB
"""
from datetime import datetime
from typing import Dict, List, Optional

# In-memory storage (resets when server restarts)
users_db: Dict[str, dict] = {}
tasks_db: Dict[int, dict] = {}
task_id_counter = 1


def create_user(username: str, email: str, hashed_password: str) -> dict:
    """
    Create a new user in the database
    
    Args:
        username: Unique username
        email: User email
        hashed_password: Hashed password
        
    Returns:
        Created user data
    """
    user = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow()
    }
    users_db[username] = user
    return user


def get_user_by_username(username: str) -> Optional[dict]:
    """
    Get user by username
    
    Args:
        username: Username to search for
        
    Returns:
        User data or None if not found
    """
    return users_db.get(username)


def get_user_by_email(email: str) -> Optional[dict]:
    """
    Get user by email
    
    Args:
        email: Email to search for
        
    Returns:
        User data or None if not found
    """
    for user in users_db.values():
        if user["email"] == email:
            return user
    return None


def create_task(title: str, description: Optional[str], priority: str, 
                completed: bool, owner: str) -> dict:
    """
    Create a new task
    
    Args:
        title: Task title
        description: Task description
        priority: Task priority (low, medium, high)
        completed: Completion status
        owner: Username of task owner
        
    Returns:
        Created task data
    """
    global task_id_counter
    
    task = {
        "id": task_id_counter,
        "title": title,
        "description": description,
        "priority": priority,
        "completed": completed,
        "owner": owner,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    tasks_db[task_id_counter] = task
    task_id_counter += 1
    
    return task


def get_task_by_id(task_id: int) -> Optional[dict]:
    """
    Get task by ID
    
    Args:
        task_id: Task ID
        
    Returns:
        Task data or None if not found
    """
    return tasks_db.get(task_id)


def get_tasks_by_owner(owner: str) -> List[dict]:
    """
    Get all tasks for a specific owner
    
    Args:
        owner: Username of the owner
        
    Returns:
        List of tasks
    """
    return [task for task in tasks_db.values() if task["owner"] == owner]


def update_task(task_id: int, updates: dict) -> Optional[dict]:
    """
    Update a task
    
    Args:
        task_id: Task ID to update
        updates: Dictionary of fields to update
        
    Returns:
        Updated task data or None if not found
    """
    task = tasks_db.get(task_id)
    if not task:
        return None
    
    # Update fields
    for key, value in updates.items():
        if value is not None:  # Only update non-None values
            task[key] = value
    
    task["updated_at"] = datetime.utcnow()
    return task


def delete_task(task_id: int) -> bool:
    """
    Delete a task
    
    Args:
        task_id: Task ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    if task_id in tasks_db:
        del tasks_db[task_id]
        return True
    return False


def reset_database():
    """Reset the database (useful for testing)"""
    global task_id_counter
    users_db.clear()
    tasks_db.clear()
    task_id_counter = 1
