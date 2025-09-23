"""
Tests for user management endpoints.

This module tests:
- User listing and retrieval
- User status management
- User deletion and deactivation
- Admin user operations
- User search and filtering
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class TestUserListing:
    """Test user listing and retrieval functionality."""
    
    async def test_list_users_as_admin(self, test_client: AsyncClient, admin_headers: dict, test_user: User):
        """Test listing users as admin."""
        response = await test_client.get("/users/", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find our test user
        test_user_data = next((u for u in data if u["id"] == test_user.id), None)
        assert test_user_data is not None
        assert test_user_data["email"] == test_user.email
        assert test_user_data["full_name"] == test_user.full_name
        assert test_user_data["is_active"] == test_user.is_active
        assert "password_hash" not in test_user_data  # Password should not be exposed
    
    async def test_list_users_with_pagination(self, test_client: AsyncClient, admin_headers: dict):
        """Test listing users with pagination."""
        response = await test_client.get("/users/?skip=0&limit=5", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    async def test_list_users_as_regular_user_fails(self, test_client: AsyncClient, auth_headers: dict):
        """Test that regular users cannot list all users."""
        response = await test_client.get("/users/", headers=auth_headers)
        
        assert response.status_code == 403
        assert "Administrator privileges required" in response.json()["detail"]
    
    async def test_get_user_by_id_as_admin(self, test_client: AsyncClient, admin_headers: dict, test_user: User):
        """Test getting specific user by ID as admin."""
        response = await test_client.get(f"/users/{test_user.id}", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert "password_hash" not in data
    
    async def test_get_own_user_info(self, test_client: AsyncClient, auth_headers: dict, test_user: User):
        """Test that users can get their own information."""
        response = await test_client.get(f"/users/{test_user.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
    
    async def test_get_other_user_info_as_regular_user_fails(self, test_client: AsyncClient, auth_headers: dict, admin_user: User):
        """Test that regular users cannot get other users' information."""
        response = await test_client.get(f"/users/{admin_user.id}", headers=auth_headers)
        
        assert response.status_code == 403
    
    async def test_get_nonexistent_user_fails(self, test_client: AsyncClient, admin_headers: dict):
        """Test getting non-existent user fails."""
        response = await test_client.get("/users/99999", headers=admin_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUserStatusManagement:
    """Test user activation/deactivation functionality."""
    
    async def test_deactivate_user_as_admin(self, test_client: AsyncClient, admin_headers: dict, test_user: User, db_session: AsyncSession):
        """Test deactivating user as admin."""
        response = await test_client.put(f"/users/{test_user.id}/deactivate", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert "deactivated successfully" in data["message"]
        
        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.is_active is False
    
    async def test_activate_user_as_admin(self, test_client: AsyncClient, admin_headers: dict, db_session: AsyncSession):
        """Test activating user as admin."""
        # First create an inactive user
        inactive_user = User(
            email="inactive@test.com",
            password_hash="hashed",
            full_name="Inactive User",
            is_active=False
        )
        db_session.add(inactive_user)
        await db_session.commit()
        await db_session.refresh(inactive_user)
        
        response = await test_client.put(f"/users/{inactive_user.id}/activate", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
        assert "activated successfully" in data["message"]
        
        # Verify in database
        await db_session.refresh(inactive_user)
        assert inactive_user.is_active is True
    
    async def test_deactivate_user_as_regular_user_fails(self, test_client: AsyncClient, auth_headers: dict, admin_user: User):
        """Test that regular users cannot deactivate other users."""
        response = await test_client.put(f"/users/{admin_user.id}/deactivate", headers=auth_headers)
        
        assert response.status_code == 403
    
    async def test_user_cannot_deactivate_self(self, test_client: AsyncClient, auth_headers: dict, test_user: User):
        """Test that users cannot deactivate themselves."""
        response = await test_client.put(f"/users/{test_user.id}/deactivate", headers=auth_headers)
        
        assert response.status_code == 403
        assert "cannot deactivate yourself" in response.json()["detail"]
    
    async def test_deactivate_nonexistent_user_fails(self, test_client: AsyncClient, admin_headers: dict):
        """Test deactivating non-existent user fails."""
        response = await test_client.put("/users/99999/deactivate", headers=admin_headers)
        
        assert response.status_code == 404


class TestUserDeletion:
    """Test user deletion functionality."""
    
    async def test_delete_user_as_admin(self, test_client: AsyncClient, admin_headers: dict, db_session: AsyncSession):
        """Test deleting user as admin."""
        # Create a user to delete
        user_to_delete = User(
            email="todelete@test.com",
            password_hash="hashed",
            full_name="To Delete User"
        )
        db_session.add(user_to_delete)
        await db_session.commit()
        await db_session.refresh(user_to_delete)
        user_id = user_to_delete.id
        
        response = await test_client.delete(f"/users/{user_id}", headers=admin_headers)
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify user is deleted from database
        result = await db_session.execute(select(User).where(User.id == user_id))
        deleted_user = result.scalar_one_or_none()
        assert deleted_user is None
    
    async def test_delete_user_as_regular_user_fails(self, test_client: AsyncClient, auth_headers: dict, admin_user: User):
        """Test that regular users cannot delete other users."""
        response = await test_client.delete(f"/users/{admin_user.id}", headers=auth_headers)
        
        assert response.status_code == 403
    
    async def test_user_cannot_delete_self(self, test_client: AsyncClient, auth_headers: dict, test_user: User):
        """Test that users cannot delete themselves."""
        response = await test_client.delete(f"/users/{test_user.id}", headers=auth_headers)
        
        assert response.status_code == 403
        assert "cannot delete yourself" in response.json()["detail"]
    
    async def test_delete_nonexistent_user_fails(self, test_client: AsyncClient, admin_headers: dict):
        """Test deleting non-existent user fails."""
        response = await test_client.delete("/users/99999", headers=admin_headers)
        
        assert response.status_code == 404


class TestUserSearch:
    """Test user search and filtering functionality."""
    
    async def test_search_users_by_email(self, test_client: AsyncClient, admin_headers: dict, test_user: User):
        """Test searching users by email."""
        search_term = test_user.email.split("@")[0]  # Get username part
        response = await test_client.get(f"/users/?search={search_term}", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should find our test user
        found_user = next((u for u in data if u["id"] == test_user.id), None)
        assert found_user is not None
    
    async def test_search_users_by_name(self, test_client: AsyncClient, admin_headers: dict, test_user: User):
        """Test searching users by name."""
        search_term = test_user.full_name.split()[0]  # Get first name
        response = await test_client.get(f"/users/?search={search_term}", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should find our test user
        found_user = next((u for u in data if u["id"] == test_user.id), None)
        assert found_user is not None
    
    async def test_filter_active_users_only(self, test_client: AsyncClient, admin_headers: dict, db_session: AsyncSession):
        """Test filtering to show only active users."""
        # Create an inactive user
        inactive_user = User(
            email="inactive2@test.com",
            password_hash="hashed",
            full_name="Inactive User 2",
            is_active=False
        )
        db_session.add(inactive_user)
        await db_session.commit()
        
        response = await test_client.get("/users/?active_only=true", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned users should be active
        assert all(user["is_active"] for user in data)
        # Should not include our inactive user
        assert not any(user["email"] == "inactive2@test.com" for user in data)
    
    async def test_filter_inactive_users_only(self, test_client: AsyncClient, admin_headers: dict, db_session: AsyncSession):
        """Test filtering to show only inactive users."""
        # Create an inactive user
        inactive_user = User(
            email="inactive3@test.com",
            password_hash="hashed",
            full_name="Inactive User 3",
            is_active=False
        )
        db_session.add(inactive_user)
        await db_session.commit()
        
        response = await test_client.get("/users/?active_only=false", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should include our inactive user
        assert any(user["email"] == "inactive3@test.com" for user in data)


class TestAdminUserOperations:
    """Test operations specific to admin users."""
    
    async def test_promote_user_to_admin(self, test_client: AsyncClient, admin_headers: dict, test_user: User, db_session: AsyncSession):
        """Test promoting user to admin status."""
        response = await test_client.put(f"/users/{test_user.id}/make-admin", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] is True
        assert "promoted to admin" in data["message"]
        
        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.is_admin is True
    
    async def test_demote_admin_user(self, test_client: AsyncClient, admin_headers: dict, db_session: AsyncSession):
        """Test demoting admin user to regular user."""
        # Create an admin user to demote
        admin_to_demote = User(
            email="admintodemote@test.com",
            password_hash="hashed",
            full_name="Admin To Demote",
            is_admin=True
        )
        db_session.add(admin_to_demote)
        await db_session.commit()
        await db_session.refresh(admin_to_demote)
        
        response = await test_client.put(f"/users/{admin_to_demote.id}/remove-admin", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] is False
        assert "removed from admin" in data["message"]
        
        # Verify in database
        await db_session.refresh(admin_to_demote)
        assert admin_to_demote.is_admin is False
    
    async def test_admin_cannot_demote_self(self, test_client: AsyncClient, admin_headers: dict, admin_user: User):
        """Test that admin cannot demote themselves."""
        response = await test_client.put(f"/users/{admin_user.id}/remove-admin", headers=admin_headers)
        
        assert response.status_code == 400
        assert "cannot remove admin privileges from yourself" in response.json()["detail"]
    
    async def test_regular_user_cannot_promote_users(self, test_client: AsyncClient, auth_headers: dict, admin_user: User):
        """Test that regular users cannot promote other users to admin."""
        response = await test_client.put(f"/users/{admin_user.id}/make-admin", headers=auth_headers)
        
        assert response.status_code == 403


class TestUserDataValidation:
    """Test user data validation and edge cases."""
    
    async def test_create_user_with_existing_email_fails(self, test_client: AsyncClient, admin_headers: dict, test_user: User, test_data):
        """Test creating user with existing email fails."""
        user_data = test_data.user_registration_data()
        user_data["email"] = test_user.email  # Use existing email
        
        response = await test_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    async def test_create_user_with_invalid_email_fails(self, test_client: AsyncClient, test_data):
        """Test creating user with invalid email fails."""
        user_data = test_data.user_registration_data()
        user_data["email"] = "invalid-email"
        
        response = await test_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    async def test_create_user_with_weak_password_fails(self, test_client: AsyncClient, test_data):
        """Test creating user with weak password fails."""
        user_data = test_data.user_registration_data()
        user_data["password"] = "123"  # Too weak
        
        response = await test_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error


class TestUserBulkOperations:
    """Test bulk operations on users."""
    
    async def test_bulk_deactivate_users(self, test_client: AsyncClient, admin_headers: dict, db_session: AsyncSession):
        """Test bulk deactivating multiple users."""
        # Create multiple users to deactivate
        users_to_deactivate = []
        for i in range(3):
            user = User(
                email=f"bulk{i}@test.com",
                password_hash="hashed",
                full_name=f"Bulk User {i}"
            )
            db_session.add(user)
            users_to_deactivate.append(user)
        
        await db_session.commit()
        for user in users_to_deactivate:
            await db_session.refresh(user)
        
        user_ids = [user.id for user in users_to_deactivate]
        bulk_data = {"user_ids": user_ids}
        
        response = await test_client.put("/users/bulk/deactivate", json=bulk_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["deactivated_count"] == 3
        assert "users deactivated successfully" in data["message"]
        
        # Verify all users are deactivated
        for user in users_to_deactivate:
            await db_session.refresh(user)
            assert user.is_active is False
    
    async def test_bulk_delete_users(self, test_client: AsyncClient, admin_headers: dict, db_session: AsyncSession):
        """Test bulk deleting multiple users."""
        # Create multiple users to delete
        users_to_delete = []
        for i in range(2):
            user = User(
                email=f"bulkdelete{i}@test.com",
                password_hash="hashed",
                full_name=f"Bulk Delete User {i}"
            )
            db_session.add(user)
            users_to_delete.append(user)
        
        await db_session.commit()
        for user in users_to_delete:
            await db_session.refresh(user)
        
        user_ids = [user.id for user in users_to_delete]
        bulk_data = {"user_ids": user_ids}
        
        response = await test_client.put("/users/bulk/delete", json=bulk_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 2
        assert "users deleted successfully" in data["message"]
        
        # Verify all users are deleted
        for user_id in user_ids:
            result = await db_session.execute(select(User).where(User.id == user_id))
            deleted_user = result.scalar_one_or_none()
            assert deleted_user is None
    
    async def test_bulk_operations_require_admin(self, test_client: AsyncClient, auth_headers: dict):
        """Test that bulk operations require admin privileges."""
        bulk_data = {"user_ids": [1, 2, 3]}
        
        response = await test_client.put("/users/bulk/deactivate", json=bulk_data, headers=auth_headers)
        assert response.status_code == 403
        
        response = await test_client.put("/users/bulk/delete", json=bulk_data, headers=auth_headers)
        assert response.status_code == 403
