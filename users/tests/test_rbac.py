"""
Tests for Role-Based Access Control (RBAC) endpoints.

This module tests:
- Permission management
- Role management  
- User role assignments
- Permission checking
- Access control enforcement
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.rbac_models import Role, Permission


class TestPermissionManagement:
    """Test permission management endpoints."""
    
    async def test_create_permission_as_admin(self, test_client: AsyncClient, admin_headers: dict, test_data):
        """Test creating a permission as admin."""
        permission_data = test_data.permission_create_data()
        
        response = await test_client.post("/rbac/permissions", json=permission_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == permission_data["name"]
        assert data["description"] == permission_data["description"]
        assert data["resource"] == permission_data["resource"]
        assert data["action"] == permission_data["action"]
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_permission_as_user_fails(self, test_client: AsyncClient, auth_headers: dict, test_data):
        """Test creating permission as regular user fails."""
        permission_data = test_data.permission_create_data()
        
        response = await test_client.post("/rbac/permissions", json=permission_data, headers=auth_headers)
        
        assert response.status_code == 403
        assert "Administrator privileges required" in response.json()["detail"]
    
    async def test_create_duplicate_permission_fails(self, test_client: AsyncClient, admin_headers: dict, test_permission: Permission):
        """Test creating duplicate permission fails."""
        duplicate_data = {
            "name": test_permission.name,
            "description": "Duplicate permission",
            "resource": test_permission.resource,
            "action": test_permission.action
        }
        
        response = await test_client.post("/rbac/permissions", json=duplicate_data, headers=admin_headers)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    async def test_list_permissions_as_admin(self, test_client: AsyncClient, admin_headers: dict, test_permission: Permission):
        """Test listing permissions as admin."""
        response = await test_client.get("/rbac/permissions", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Find our test permission
        test_perm = next((p for p in data if p["id"] == test_permission.id), None)
        assert test_perm is not None
        assert test_perm["name"] == test_permission.name
    
    async def test_list_permissions_with_pagination(self, test_client: AsyncClient, admin_headers: dict):
        """Test listing permissions with pagination."""
        response = await test_client.get("/rbac/permissions?skip=0&limit=5", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    async def test_delete_permission_as_admin(self, test_client: AsyncClient, admin_headers: dict, test_permission: Permission):
        """Test deleting permission as admin."""
        response = await test_client.delete(f"/rbac/permissions/{test_permission.id}", headers=admin_headers)
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify permission is deleted
        get_response = await test_client.get("/rbac/permissions", headers=admin_headers)
        permissions = get_response.json()
        assert not any(p["id"] == test_permission.id for p in permissions)
    
    async def test_delete_nonexistent_permission_fails(self, test_client: AsyncClient, admin_headers: dict):
        """Test deleting non-existent permission fails."""
        response = await test_client.delete("/rbac/permissions/99999", headers=admin_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestRoleManagement:
    """Test role management endpoints."""
    
    async def test_create_role_as_admin(self, test_client: AsyncClient, admin_headers: dict, test_permission: Permission, test_data):
        """Test creating a role as admin."""
        role_data = test_data.role_create_data(permission_ids=[test_permission.id])
        
        response = await test_client.post("/rbac/roles", json=role_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == role_data["name"]
        assert data["description"] == role_data["description"]
        assert data["is_default"] == role_data["is_default"]
        assert len(data["permissions"]) == 1
        assert data["permissions"][0]["id"] == test_permission.id
    
    async def test_create_role_without_permissions(self, test_client: AsyncClient, admin_headers: dict, test_data):
        """Test creating role without permissions."""
        role_data = test_data.role_create_data(permission_ids=[])
        
        response = await test_client.post("/rbac/roles", json=role_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["permissions"]) == 0
    
    async def test_create_duplicate_role_fails(self, test_client: AsyncClient, admin_headers: dict, test_role: Role):
        """Test creating duplicate role fails."""
        duplicate_data = {
            "name": test_role.name,
            "description": "Duplicate role",
            "is_default": False,
            "permission_ids": []
        }
        
        response = await test_client.post("/rbac/roles", json=duplicate_data, headers=admin_headers)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    async def test_list_roles_as_admin(self, test_client: AsyncClient, admin_headers: dict, test_role: Role):
        """Test listing roles as admin."""
        response = await test_client.get("/rbac/roles", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Find our test role
        test_role_data = next((r for r in data if r["id"] == test_role.id), None)
        assert test_role_data is not None
        assert test_role_data["name"] == test_role.name
    
    async def test_get_role_by_id(self, test_client: AsyncClient, admin_headers: dict, test_role: Role):
        """Test getting specific role by ID."""
        response = await test_client.get(f"/rbac/roles/{test_role.id}", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_role.id
        assert data["name"] == test_role.name
        assert "permissions" in data
    
    async def test_get_nonexistent_role_fails(self, test_client: AsyncClient, admin_headers: dict):
        """Test getting non-existent role fails."""
        response = await test_client.get("/rbac/roles/99999", headers=admin_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    async def test_update_role(self, test_client: AsyncClient, admin_headers: dict, test_role: Role, test_permission: Permission):
        """Test updating role."""
        update_data = {
            "description": "Updated description",
            "permission_ids": [test_permission.id]
        }
        
        response = await test_client.put(f"/rbac/roles/{test_role.id}", json=update_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]
        assert len(data["permissions"]) == 1
    
    async def test_delete_role(self, test_client: AsyncClient, admin_headers: dict, test_role: Role):
        """Test deleting role."""
        response = await test_client.delete(f"/rbac/roles/{test_role.id}", headers=admin_headers)
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]


class TestUserRoleAssignment:
    """Test user role assignment functionality."""
    
    async def test_assign_roles_to_user(self, test_client: AsyncClient, admin_headers: dict, test_user: User, test_role: Role):
        """Test assigning roles to user."""
        assignment_data = {
            "user_id": test_user.id,
            "role_ids": [test_role.id]
        }
        
        response = await test_client.post(f"/rbac/users/{test_user.id}/roles", json=assignment_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id
        assert len(data["roles"]) == 1
        assert data["roles"][0]["id"] == test_role.id
        assert "assigned successfully" in data["message"]
    
    async def test_assign_roles_user_id_mismatch_fails(self, test_client: AsyncClient, admin_headers: dict, test_user: User, test_role: Role):
        """Test assigning roles with mismatched user ID fails."""
        assignment_data = {
            "user_id": 999,  # Different from URL
            "role_ids": [test_role.id]
        }
        
        response = await test_client.post(f"/rbac/users/{test_user.id}/roles", json=assignment_data, headers=admin_headers)
        
        assert response.status_code == 400
        assert "mismatch" in response.json()["detail"]
    
    async def test_assign_roles_to_nonexistent_user_fails(self, test_client: AsyncClient, admin_headers: dict, test_role: Role):
        """Test assigning roles to non-existent user fails."""
        assignment_data = {
            "user_id": 99999,
            "role_ids": [test_role.id]
        }
        
        response = await test_client.post("/rbac/users/99999/roles", json=assignment_data, headers=admin_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    async def test_get_user_roles(self, test_client: AsyncClient, admin_headers: dict, user_with_role: User, test_role: Role):
        """Test getting user's roles."""
        response = await test_client.get(f"/rbac/users/{user_with_role.id}/roles", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(role["id"] == test_role.id for role in data)
    
    async def test_list_users_with_roles(self, test_client: AsyncClient, admin_headers: dict, user_with_role: User):
        """Test listing all users with their roles."""
        response = await test_client.get("/rbac/users", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Find our test user
        test_user_data = next((u for u in data if u["id"] == user_with_role.id), None)
        assert test_user_data is not None
        assert "roles" in test_user_data
        assert len(test_user_data["roles"]) >= 1


class TestPermissionChecking:
    """Test permission checking functionality."""
    
    async def test_check_permission_as_admin(self, test_client: AsyncClient, admin_headers: dict):
        """Test checking permission as admin."""
        permission_check = {
            "resource": "user",
            "action": "read"
        }
        
        response = await test_client.post("/rbac/check-permission", json=permission_check, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_permission"] is True  # Admin should have all permissions
        assert data["resource"] == "user"
        assert data["action"] == "read"
    
    async def test_check_permission_user_without_permission(self, test_client: AsyncClient, auth_headers: dict):
        """Test checking permission for user without that permission."""
        permission_check = {
            "resource": "admin",
            "action": "all"
        }
        
        # Regular user trying to check admin permission (through admin endpoint)
        # This should fail at the endpoint level since check-permission requires admin
        response = await test_client.post("/rbac/check-permission", json=permission_check, headers=auth_headers)
        
        assert response.status_code == 403


class TestAccessControlEnforcement:
    """Test that access control is properly enforced."""
    
    async def test_rbac_endpoints_require_admin(self, test_client: AsyncClient, auth_headers: dict, test_data):
        """Test that RBAC endpoints require admin privileges."""
        # Try to create permission as regular user
        permission_data = test_data.permission_create_data()
        response = await test_client.post("/rbac/permissions", json=permission_data, headers=auth_headers)
        assert response.status_code == 403
        
        # Try to list permissions as regular user
        response = await test_client.get("/rbac/permissions", headers=auth_headers)
        assert response.status_code == 403
        
        # Try to create role as regular user
        role_data = test_data.role_create_data()
        response = await test_client.post("/rbac/roles", json=role_data, headers=auth_headers)
        assert response.status_code == 403
    
    async def test_rbac_endpoints_without_auth_fail(self, test_client: AsyncClient, test_data):
        """Test that RBAC endpoints fail without authentication."""
        # Try to access without any auth
        response = await test_client.get("/rbac/permissions")
        assert response.status_code == 401
        
        response = await test_client.get("/rbac/roles")
        assert response.status_code == 401
        
        response = await test_client.get("/rbac/users")
        assert response.status_code == 401


class TestRBACModelLogic:
    """Test RBAC model business logic."""
    
    def test_permission_string_representation(self, test_permission: Permission):
        """Test permission string representation."""
        assert str(test_permission) == f"{test_permission.resource}:{test_permission.action}"
    
    def test_role_has_permission_method(self, test_role: Role, test_permission: Permission):
        """Test role has_permission method."""
        # Role should have the test permission
        assert test_role.has_permission(test_permission.resource, test_permission.action) is True
        
        # Role should not have a different permission
        assert test_role.has_permission("other", "action") is False
    
    def test_role_admin_permission(self, db_session: AsyncSession):
        """Test role with admin:all permission grants everything."""
        # This would need to be tested with a role that has admin:all permission
        # For now, just test the concept
        pass
    
    async def test_user_has_permission_through_role(self, user_with_role: User, test_permission: Permission):
        """Test user has permission through their role."""
        assert user_with_role.has_permission(test_permission.resource, test_permission.action) is True
        assert user_with_role.has_permission("other", "action") is False
    
    async def test_user_has_role_method(self, user_with_role: User, test_role: Role):
        """Test user has_role method."""
        assert user_with_role.has_role(test_role.name) is True
        assert user_with_role.has_role("nonexistent_role") is False
    
    async def test_user_is_admin_property(self, admin_user: User, test_user: User):
        """Test user is_admin property."""
        assert admin_user.is_admin is True
        assert test_user.is_admin is False
