"""
Test cases for the Secure Task Management API
Run with: pytest test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
from app import app
import database as db

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test"""
    db.reset_database()
    yield


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_register_user_success(self):
        """Test successful user registration"""
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "secure123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "password" not in data  # Password should not be in response
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        # Register first user
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test1@example.com",
                "password": "secure123"
            }
        )
        
        # Try to register with same username
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test2@example.com",
                "password": "secure456"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_login_success(self):
        """Test successful login"""
        # Register user
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "secure123"
            }
        )
        
        # Login
        response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "secure123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        # Register user
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "secure123"
            }
        )
        
        # Try to login with wrong password
        response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = client.post(
            "/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        assert response.status_code == 401


class TestProtectedRoutes:
    """Test protected routes requiring authentication"""
    
    def get_auth_token(self):
        """Helper method to register and login a user"""
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "secure123"
            }
        )
        
        response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "secure123"
            }
        )
        return response.json()["access_token"]
    
    def test_get_current_user(self):
        """Test getting current user info"""
        token = self.get_auth_token()
        
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    def test_access_protected_route_without_token(self):
        """Test accessing protected route without token"""
        response = client.get("/me")
        assert response.status_code == 403  # Forbidden
    
    def test_access_protected_route_with_invalid_token(self):
        """Test accessing protected route with invalid token"""
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401  # Unauthorized


class TestTaskManagement:
    """Test task management endpoints"""
    
    def get_auth_token(self):
        """Helper method to register and login a user"""
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "secure123"
            }
        )
        
        response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "secure123"
            }
        )
        return response.json()["access_token"]
    
    def test_create_task(self):
        """Test creating a task"""
        token = self.get_auth_token()
        
        response = client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Test Task",
                "description": "Test Description",
                "priority": "high",
                "completed": False
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["priority"] == "high"
        assert data["owner"] == "testuser"
    
    def test_get_tasks(self):
        """Test getting all tasks for user"""
        token = self.get_auth_token()
        
        # Create a task
        client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Task 1",
                "priority": "medium"
            }
        )
        
        # Get all tasks
        response = client.get(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Task 1"
    
    def test_get_specific_task(self):
        """Test getting a specific task"""
        token = self.get_auth_token()
        
        # Create a task
        create_response = client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Test Task",
                "priority": "low"
            }
        )
        task_id = create_response.json()["id"]
        
        # Get the task
        response = client.get(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"
    
    def test_update_task(self):
        """Test updating a task"""
        token = self.get_auth_token()
        
        # Create a task
        create_response = client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Original Title",
                "priority": "low"
            }
        )
        task_id = create_response.json()["id"]
        
        # Update the task
        response = client.put(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Updated Title",
                "completed": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["completed"] is True
    
    def test_delete_task(self):
        """Test deleting a task"""
        token = self.get_auth_token()
        
        # Create a task
        create_response = client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Task to Delete",
                "priority": "medium"
            }
        )
        task_id = create_response.json()["id"]
        
        # Delete the task
        response = client.delete(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Verify task is deleted
        get_response = client.get(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404
    
    def test_user_cannot_access_other_users_task(self):
        """Test that users cannot access other users' tasks"""
        # Create first user and task
        token1 = self.get_auth_token()
        create_response = client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {token1}"},
            json={
                "title": "User 1 Task",
                "priority": "high"
            }
        )
        task_id = create_response.json()["id"]
        
        # Create second user
        client.post(
            "/register",
            json={
                "username": "testuser2",
                "email": "test2@example.com",
                "password": "secure456"
            }
        )
        login_response = client.post(
            "/login",
            json={
                "username": "testuser2",
                "password": "secure456"
            }
        )
        token2 = login_response.json()["access_token"]
        
        # Try to access first user's task with second user's token
        response = client.get(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert response.status_code == 403  # Forbidden


class TestValidation:
    """Test input validation"""
    
    def test_register_short_password(self):
        """Test registration with short password"""
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "123"  # Too short
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_register_invalid_email(self):
        """Test registration with invalid email"""
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "not-an-email",
                "password": "secure123"
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_create_task_invalid_priority(self):
        """Test creating task with invalid priority"""
        # Register and login
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "secure123"
            }
        )
        login_response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "secure123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Try to create task with invalid priority
        response = client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Test Task",
                "priority": "urgent"  # Invalid (must be low/medium/high)
            }
        )
        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
