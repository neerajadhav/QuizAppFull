"""
Tests for authentication endpoints.

This module tests:
- User registration
- User login
- Token validation
- Protected endpoints
- Authentication edge cases
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.auth import verify_password


class TestUserRegistration:
    """Test user registration functionality."""
    
    async def test_register_new_user(self, test_client: AsyncClient, test_data):
        """Test successful user registration."""
        user_data = test_data.user_create_data()
        
        response = await test_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "id" in data
        assert "created_at" in data
        # Password should not be in response
        assert "password" not in data
        assert "hashed_password" not in data
    
    async def test_register_duplicate_email(self, test_client: AsyncClient, test_user: User, test_data):
        """Test registration with duplicate email fails."""
        user_data = test_data.user_create_data(email=test_user.email)
        
        response = await test_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    async def test_register_invalid_email(self, test_client: AsyncClient, test_data):
        """Test registration with invalid email fails."""
        user_data = test_data.user_create_data(email="invalid-email")
        
        response = await test_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    async def test_register_short_password(self, test_client: AsyncClient, test_data):
        """Test registration with short password fails."""
        user_data = test_data.user_create_data(password="short")
        
        response = await test_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    async def test_register_missing_fields(self, test_client: AsyncClient):
        """Test registration with missing required fields fails."""
        incomplete_data = {"email": "test@example.com"}
        
        response = await test_client.post("/auth/register", json=incomplete_data)
        
        assert response.status_code == 422


class TestUserLogin:
    """Test user login functionality."""
    
    async def test_login_valid_credentials(self, test_client: AsyncClient, test_user: User):
        """Test successful login with valid credentials."""
        login_data = {
            "username": test_user.email,
            "password": "testpass123"
        }
        
        response = await test_client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    async def test_login_invalid_email(self, test_client: AsyncClient):
        """Test login with non-existent email fails."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = await test_client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    async def test_login_invalid_password(self, test_client: AsyncClient, test_user: User):
        """Test login with wrong password fails."""
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        
        response = await test_client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    async def test_login_inactive_user(self, test_client: AsyncClient, inactive_user: User):
        """Test login with inactive user fails."""
        login_data = {
            "username": inactive_user.email,
            "password": "password123"
        }
        
        response = await test_client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Test protected endpoint access."""
    
    async def test_get_current_user(self, test_client: AsyncClient, test_user: User, auth_headers: dict):
        """Test getting current user information."""
        response = await test_client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
    
    async def test_protected_endpoint_without_token(self, test_client: AsyncClient):
        """Test accessing protected endpoint without token fails."""
        response = await test_client.get("/auth/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    async def test_protected_endpoint_invalid_token(self, test_client: AsyncClient):
        """Test accessing protected endpoint with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = await test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    async def test_test_token_endpoint(self, test_client: AsyncClient, test_user: User, auth_headers: dict):
        """Test the test token endpoint."""
        response = await test_client.post("/auth/test-token", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email


class TestPasswordSecurity:
    """Test password security features."""
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed."""
        from app.auth import get_password_hash, verify_password
        
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        # Hash should be verifiable
        assert verify_password(password, hashed) is True
        # Wrong password should not verify
        assert verify_password("wrongpassword", hashed) is False
    
    def test_password_hash_uniqueness(self):
        """Test that password hashes are unique for each call."""
        from app.auth import get_password_hash
        
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
