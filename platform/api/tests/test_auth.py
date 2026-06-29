"""
Auth API Tests

Tests for authentication endpoints.
"""

import pytest


class TestRegister:
    """Tests for POST /auth/register"""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={"email": "newuser@example.com", "password": "password123"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert data["message"] == "User registered successfully"
    
    def test_register_duplicate_email(self, client, registered_user, test_user_data):
        """Test registration with existing email fails."""
        response = client.post("/auth/register", json=test_user_data)
        
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email fails."""
        response = client.post(
            "/auth/register",
            json={"email": "notanemail", "password": "password123"}
        )
        
        assert response.status_code == 422
    
    def test_register_short_password(self, client):
        """Test registration with short password fails."""
        response = client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "short"}
        )
        
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /auth/login"""
    
    def test_login_success(self, client, registered_user, test_user_data):
        """Test successful login."""
        response = client.post("/auth/login", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, registered_user, test_user_data):
        """Test login with wrong password fails."""
        response = client.post(
            "/auth/login",
            json={"email": test_user_data["email"], "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user fails."""
        response = client.post(
            "/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"}
        )
        
        assert response.status_code == 401
