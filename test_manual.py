"""
Manual testing script for the Secure Task Management API
Run this script to test the API interactively

Usage: python test_manual.py
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

# ANSI color codes for pretty output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_success(message: str):
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message: str):
    print(f"{RED}✗ {message}{RESET}")


def print_info(message: str):
    print(f"{BLUE}ℹ {message}{RESET}")


def print_warning(message: str):
    print(f"{YELLOW}⚠ {message}{RESET}")


def print_json(data: dict):
    print(json.dumps(data, indent=2))


def test_health_check():
    """Test the health check endpoint"""
    print_info("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success("Health check passed")
            print_json(response.json())
        else:
            print_error(f"Health check failed: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Is the server running?")
        print_warning("Start server with: uvicorn app:app --reload")
        return False


def register_user(username: str, email: str, password: str) -> bool:
    """Register a new user"""
    print_info(f"Registering user: {username}")
    
    response = requests.post(
        f"{BASE_URL}/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    
    if response.status_code == 201:
        print_success(f"User {username} registered successfully")
        print_json(response.json())
        return True
    else:
        print_error(f"Registration failed: {response.status_code}")
        print_json(response.json())
        return False


def login_user(username: str, password: str) -> Optional[str]:
    """Login and get access token"""
    print_info(f"Logging in as: {username}")
    
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": username,
            "password": password
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        print_success(f"Login successful")
        print_info(f"Token: {token[:20]}...{token[-20:]}")
        return token
    else:
        print_error(f"Login failed: {response.status_code}")
        print_json(response.json())
        return None


def get_current_user(token: str) -> bool:
    """Get current user info"""
    print_info("Getting current user info...")
    
    response = requests.get(
        f"{BASE_URL}/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        print_success("User info retrieved")
        print_json(response.json())
        return True
    else:
        print_error(f"Failed to get user info: {response.status_code}")
        print_json(response.json())
        return False


def create_task(token: str, title: str, description: str, priority: str) -> Optional[int]:
    """Create a new task"""
    print_info(f"Creating task: {title}")
    
    response = requests.post(
        f"{BASE_URL}/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": title,
            "description": description,
            "priority": priority
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        task_id = data["id"]
        print_success(f"Task created with ID: {task_id}")
        print_json(data)
        return task_id
    else:
        print_error(f"Failed to create task: {response.status_code}")
        print_json(response.json())
        return None


def get_all_tasks(token: str) -> bool:
    """Get all tasks"""
    print_info("Getting all tasks...")
    
    response = requests.get(
        f"{BASE_URL}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        tasks = response.json()
        print_success(f"Retrieved {len(tasks)} task(s)")
        print_json(tasks)
        return True
    else:
        print_error(f"Failed to get tasks: {response.status_code}")
        print_json(response.json())
        return False


def update_task(token: str, task_id: int, completed: bool) -> bool:
    """Update a task"""
    print_info(f"Updating task {task_id}...")
    
    response = requests.put(
        f"{BASE_URL}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"completed": completed}
    )
    
    if response.status_code == 200:
        print_success(f"Task {task_id} updated")
        print_json(response.json())
        return True
    else:
        print_error(f"Failed to update task: {response.status_code}")
        print_json(response.json())
        return False


def delete_task(token: str, task_id: int) -> bool:
    """Delete a task"""
    print_info(f"Deleting task {task_id}...")
    
    response = requests.delete(
        f"{BASE_URL}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        print_success(f"Task {task_id} deleted")
        print_json(response.json())
        return True
    else:
        print_error(f"Failed to delete task: {response.status_code}")
        print_json(response.json())
        return False


def test_unauthorized_access():
    """Test accessing protected route without token"""
    print_info("Testing unauthorized access...")
    
    response = requests.get(f"{BASE_URL}/tasks")
    
    if response.status_code == 403:
        print_success("Unauthorized access correctly blocked (403)")
    else:
        print_error(f"Unexpected status code: {response.status_code}")


def test_cross_user_access(token1: str, token2: str, task_id: int):
    """Test that users cannot access each other's tasks"""
    print_info(f"Testing cross-user access for task {task_id}...")
    
    response = requests.get(
        f"{BASE_URL}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    if response.status_code == 403:
        print_success("Cross-user access correctly blocked (403)")
    else:
        print_error(f"Security issue! Got status code: {response.status_code}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🔒 Secure Task Management API - Manual Test Suite")
    print("=" * 60 + "\n")
    
    # Test 1: Health check
    print("\n--- Test 1: Health Check ---")
    if not test_health_check():
        return
    
    # Test 2: Register users
    print("\n--- Test 2: User Registration ---")
    register_user("john_doe", "john@example.com", "secure123")
    register_user("jane_smith", "jane@example.com", "password456")
    
    # Test 3: Login users
    print("\n--- Test 3: User Login ---")
    john_token = login_user("john_doe", "secure123")
    jane_token = login_user("jane_smith", "password456")
    
    if not john_token or not jane_token:
        print_error("Login failed. Cannot continue tests.")
        return
    
    # Test 4: Get current user
    print("\n--- Test 4: Get Current User ---")
    get_current_user(john_token)
    
    # Test 5: Unauthorized access
    print("\n--- Test 5: Unauthorized Access ---")
    test_unauthorized_access()
    
    # Test 6: Create tasks
    print("\n--- Test 6: Create Tasks ---")
    task1_id = create_task(john_token, "Complete training", "Finish Day 4 exercises", "high")
    task2_id = create_task(john_token, "Review security", "Study JWT and OAuth", "medium")
    task3_id = create_task(jane_token, "Deploy API", "Deploy to production", "high")
    
    # Test 7: Get all tasks
    print("\n--- Test 7: Get All Tasks (John's view) ---")
    get_all_tasks(john_token)
    
    print("\n--- Test 7b: Get All Tasks (Jane's view) ---")
    get_all_tasks(jane_token)
    
    # Test 8: Cross-user access
    if task1_id and jane_token:
        print("\n--- Test 8: Cross-User Access (Should Fail) ---")
        test_cross_user_access(john_token, jane_token, task1_id)
    
    # Test 9: Update task
    if task1_id:
        print("\n--- Test 9: Update Task ---")
        update_task(john_token, task1_id, True)
    
    # Test 10: Delete task
    if task2_id:
        print("\n--- Test 10: Delete Task ---")
        delete_task(john_token, task2_id)
    
    # Final verification
    print("\n--- Final: Verify Tasks After Deletion ---")
    get_all_tasks(john_token)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nTests interrupted by user")
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
