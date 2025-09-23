"""
Tests for user profile management endpoints.

This module tests:
- Profile retrieval
- Profile updates
- Preferences management
- Avatar management
- Profile privacy
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class TestProfileRetrieval:
    """Test profile retrieval functionality."""
    
    async def test_get_own_profile(self, test_client: AsyncClient, test_user: User, auth_headers: dict):
        """Test getting own profile."""
        response = await test_client.get("/profile/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "bio" in data
        assert "avatar_url" in data
        assert "location" in data
        assert "website" in data
        assert "phone" in data
        assert "preferences" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    async def test_get_profile_without_auth(self, test_client: AsyncClient):
        """Test getting profile without authentication fails."""
        response = await test_client.get("/profile/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    async def test_get_other_user_profile(self, test_client: AsyncClient, test_user: User, admin_user: User, auth_headers: dict):
        """Test getting another user's profile."""
        response = await test_client.get(f"/profile/{admin_user.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == admin_user.id
        assert data["email"] == admin_user.email
    
    async def test_get_nonexistent_profile(self, test_client: AsyncClient, auth_headers: dict):
        """Test getting non-existent user profile fails."""
        response = await test_client.get("/profile/99999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    async def test_get_inactive_user_profile(self, test_client: AsyncClient, inactive_user: User, auth_headers: dict):
        """Test getting inactive user profile fails."""
        response = await test_client.get(f"/profile/{inactive_user.id}", headers=auth_headers)
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


class TestProfileUpdates:
    """Test profile update functionality."""
    
    async def test_update_profile_basic_info(self, test_client: AsyncClient, test_user: User, auth_headers: dict, test_data):
        """Test updating basic profile information."""
        update_data = test_data.profile_update_data()
        
        response = await test_client.put("/profile/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == update_data["bio"]
        assert data["location"] == update_data["location"]
        assert data["website"] == update_data["website"]
    
    async def test_update_profile_partial(self, test_client: AsyncClient, test_user: User, auth_headers: dict):
        """Test partial profile update."""
        update_data = {"bio": "New bio only"}
        
        response = await test_client.put("/profile/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == update_data["bio"]
        # Other fields should remain unchanged
        assert data["username"] == test_user.username
    
    async def test_update_profile_invalid_website(self, test_client: AsyncClient, auth_headers: dict):
        """Test updating profile with invalid website URL."""
        update_data = {"website": "not-a-valid-url"}
        
        response = await test_client.put("/profile/me", json=update_data, headers=auth_headers)
        
        # Should still succeed but with validation warning or sanitization
        assert response.status_code == 200
    
    async def test_update_profile_invalid_phone(self, test_client: AsyncClient, auth_headers: dict):
        """Test updating profile with invalid phone number."""
        update_data = {"phone": "invalid-phone-format"}
        
        response = await test_client.put("/profile/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    async def test_update_profile_long_bio(self, test_client: AsyncClient, auth_headers: dict):
        """Test updating profile with bio that's too long."""
        update_data = {"bio": "x" * 1001}  # Assuming 1000 char limit
        
        response = await test_client.put("/profile/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    async def test_update_profile_without_auth(self, test_client: AsyncClient, test_data):
        """Test updating profile without authentication fails."""
        update_data = test_data.profile_update_data()
        
        response = await test_client.put("/profile/me", json=update_data)
        
        assert response.status_code == 401


class TestPreferencesManagement:
    """Test user preferences functionality."""
    
    async def test_get_initial_preferences(self, test_client: AsyncClient, test_user: User, auth_headers: dict):
        """Test getting initial empty preferences."""
        response = await test_client.get("/profile/me/preferences", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "preferences" in data
        assert "user_id" in data
        assert data["user_id"] == test_user.id
    
    async def test_update_preferences(self, test_client: AsyncClient, auth_headers: dict):
        """Test updating user preferences."""
        preferences_data = {
            "theme": "dark",
            "language": "en",
            "notifications_email": True,
            "notifications_sms": False
        }
        
        response = await test_client.put("/profile/me/preferences", json=preferences_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Preferences updated successfully"
        assert "preferences" in data
        assert data["preferences"]["theme"] == "dark"
        assert data["preferences"]["language"] == "en"
    
    async def test_update_preferences_partial(self, test_client: AsyncClient, auth_headers: dict):
        """Test partial preferences update."""
        # First set some preferences
        initial_prefs = {"theme": "light", "language": "en"}
        await test_client.put("/profile/me/preferences", json=initial_prefs, headers=auth_headers)
        
        # Then update only one
        update_prefs = {"theme": "dark"}
        response = await test_client.put("/profile/me/preferences", json=update_prefs, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["preferences"]["theme"] == "dark"
        assert data["preferences"]["language"] == "en"  # Should be preserved
    
    async def test_update_preferences_invalid_theme(self, test_client: AsyncClient, auth_headers: dict):
        """Test updating preferences with invalid theme."""
        preferences_data = {"theme": "invalid_theme"}
        
        response = await test_client.put("/profile/me/preferences", json=preferences_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    async def test_preferences_without_auth(self, test_client: AsyncClient):
        """Test accessing preferences without authentication fails."""
        response = await test_client.get("/profile/me/preferences")
        
        assert response.status_code == 401


class TestAvatarManagement:
    """Test avatar management functionality."""
    
    async def test_remove_avatar(self, test_client: AsyncClient, test_user: User, auth_headers: dict, db_session: AsyncSession):
        """Test removing user avatar."""
        # First set an avatar
        test_user.avatar_url = "https://example.com/avatar.jpg"
        await db_session.commit()
        
        response = await test_client.delete("/profile/me/avatar", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Avatar removed successfully"
        
        # Verify avatar was removed
        profile_response = await test_client.get("/profile/me", headers=auth_headers)
        profile_data = profile_response.json()
        assert profile_data["avatar_url"] is None
    
    async def test_remove_avatar_when_none_exists(self, test_client: AsyncClient, auth_headers: dict):
        """Test removing avatar when none exists."""
        response = await test_client.delete("/profile/me/avatar", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Avatar removed successfully"
    
    async def test_remove_avatar_without_auth(self, test_client: AsyncClient):
        """Test removing avatar without authentication fails."""
        response = await test_client.delete("/profile/me/avatar")
        
        assert response.status_code == 401


class TestProfileValidation:
    """Test profile data validation."""
    
    async def test_profile_update_with_empty_data(self, test_client: AsyncClient, auth_headers: dict):
        """Test profile update with empty data."""
        response = await test_client.put("/profile/me", json={}, headers=auth_headers)
        
        assert response.status_code == 200
        # Empty update should succeed but change nothing
    
    async def test_profile_update_with_null_values(self, test_client: AsyncClient, auth_headers: dict):
        """Test profile update with null values to clear fields."""
        update_data = {
            "bio": None,
            "location": None,
            "website": None
        }
        
        response = await test_client.put("/profile/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] is None
        assert data["location"] is None
        assert data["website"] is None
    
    async def test_profile_username_update_validation(self, test_client: AsyncClient, auth_headers: dict):
        """Test that username update has proper validation."""
        update_data = {"username": "a" * 256}  # Too long
        
        response = await test_client.put("/profile/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 422
