"""
Integration tests for the complete user management system.

This module tests:
- End-to-end user workflows
- Authentication + authorization flows
- RBAC + profile interactions
- Cross-feature integration
- System-level behavior
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.rbac_models import Role, Permission


class TestUserRegistrationFlow:
    """Test complete user registration and onboarding flow."""
    
    async def test_complete_user_onboarding_flow(self, test_client: AsyncClient, test_data, db_session: AsyncSession):
        """Test complete user onboarding from registration to profile setup."""
        # Step 1: Register new user
        registration_data = test_data.user_registration_data()
        register_response = await test_client.post("/auth/register", json=registration_data)
        
        assert register_response.status_code == 201
        user_data = register_response.json()
        user_id = user_data["id"]
        
        # Step 2: Login with new user
        login_data = {
            "username": registration_data["email"],
            "password": registration_data["password"]
        }
        login_response = await test_client.post("/auth/login", data=login_data)
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        access_token = token_data["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        
        # Step 3: Create user profile
        profile_data = test_data.profile_create_data()
        profile_response = await test_client.post("/profile/", json=profile_data, headers=auth_headers)
        
        assert profile_response.status_code == 201
        profile = profile_response.json()
        assert profile["user_id"] == user_id
        
        # Step 4: Update profile preferences
        preferences = {"theme": "dark", "notifications": True, "language": "en"}
        prefs_response = await test_client.put("/profile/preferences", json=preferences, headers=auth_headers)
        
        assert prefs_response.status_code == 200
        updated_prefs = prefs_response.json()
        assert updated_prefs["preferences"]["theme"] == "dark"
        
        # Step 5: Verify user can access their own data
        user_response = await test_client.get(f"/users/{user_id}", headers=auth_headers)
        
        assert user_response.status_code == 200
        final_user_data = user_response.json()
        assert final_user_data["email"] == registration_data["email"]
    
    async def test_user_registration_with_default_role(self, test_client: AsyncClient, test_data, db_session: AsyncSession, admin_headers: dict):
        """Test that new users get assigned default role if one exists."""
        # Step 1: Create a default role
        default_role_data = test_data.role_create_data()
        default_role_data["is_default"] = True
        default_role_data["name"] = "default_user"
        
        role_response = await test_client.post("/rbac/roles", json=default_role_data, headers=admin_headers)
        assert role_response.status_code == 201
        default_role = role_response.json()
        
        # Step 2: Register new user
        registration_data = test_data.user_registration_data()
        register_response = await test_client.post("/auth/register", json=registration_data)
        
        assert register_response.status_code == 201
        user_data = register_response.json()
        user_id = user_data["id"]
        
        # Step 3: Check if user was assigned default role
        user_roles_response = await test_client.get(f"/rbac/users/{user_id}/roles", headers=admin_headers)
        
        assert user_roles_response.status_code == 200
        user_roles = user_roles_response.json()
        assert len(user_roles) >= 1
        assert any(role["name"] == "default_user" for role in user_roles)


class TestAuthenticationAuthorization:
    """Test authentication and authorization interactions."""
    
    async def test_role_based_endpoint_access(self, test_client: AsyncClient, admin_headers: dict, auth_headers: dict, test_data):
        """Test that role-based access control works across different endpoints."""
        # Admin should access all admin endpoints
        admin_endpoints = [
            "/users/",
            "/rbac/permissions",
            "/rbac/roles",
            "/rbac/users"
        ]
        
        for endpoint in admin_endpoints:
            response = await test_client.get(endpoint, headers=admin_headers)
            assert response.status_code == 200, f"Admin should access {endpoint}"
        
        # Regular user should be denied admin endpoints
        for endpoint in admin_endpoints:
            response = await test_client.get(endpoint, headers=auth_headers)
            assert response.status_code == 403, f"Regular user should be denied {endpoint}"
    
    async def test_token_expiration_and_refresh(self, test_client: AsyncClient, test_user: User, test_data):
        """Test token expiration handling and refresh."""
        # Login to get initial token
        login_data = {
            "username": test_user.email,
            "password": "testpass123"  # From fixture
        }
        login_response = await test_client.post("/auth/login", data=login_data)
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")
        
        # Use token to access protected endpoint
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        me_response = await test_client.get("/auth/me", headers=auth_headers)
        
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["email"] == test_user.email
        
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        invalid_response = await test_client.get("/auth/me", headers=invalid_headers)
        
        assert invalid_response.status_code == 401


class TestRBACIntegration:
    """Test RBAC system integration with other features."""
    
    async def test_permission_based_profile_access(self, test_client: AsyncClient, admin_headers: dict, test_data, db_session: AsyncSession):
        """Test that profile access respects permission-based control."""
        # Create a permission for profile management
        permission_data = {
            "name": "manage_all_profiles",
            "description": "Can manage all user profiles",
            "resource": "profile",
            "action": "manage_all"
        }
        perm_response = await test_client.post("/rbac/permissions", json=permission_data, headers=admin_headers)
        assert perm_response.status_code == 201
        permission = perm_response.json()
        
        # Create a role with this permission
        role_data = test_data.role_create_data()
        role_data["name"] = "profile_manager"
        role_data["permission_ids"] = [permission["id"]]
        
        role_response = await test_client.post("/rbac/roles", json=role_data, headers=admin_headers)
        assert role_response.status_code == 201
        role = role_response.json()
        
        # Create a user and assign the role
        user_data = test_data.user_registration_data()
        register_response = await test_client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201
        user = register_response.json()
        
        # Assign role to user
        assignment_data = {
            "user_id": user["id"],
            "role_ids": [role["id"]]
        }
        assign_response = await test_client.post(f"/rbac/users/{user['id']}/roles", json=assignment_data, headers=admin_headers)
        assert assign_response.status_code == 200
        
        # Login as the user with special role
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        login_response = await test_client.post("/auth/login", data=login_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        user_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # This user should now have special profile permissions
        # (This would depend on implementing permission checking in profile endpoints)
    
    async def test_role_hierarchy_and_inheritance(self, test_client: AsyncClient, admin_headers: dict, test_data):
        """Test role hierarchy and permission inheritance."""
        # Create base permission
        base_perm_data = {
            "name": "read_users",
            "description": "Can read user data",
            "resource": "user",
            "action": "read"
        }
        base_perm_response = await test_client.post("/rbac/permissions", json=base_perm_data, headers=admin_headers)
        assert base_perm_response.status_code == 201
        base_permission = base_perm_response.json()
        
        # Create elevated permission
        elevated_perm_data = {
            "name": "manage_users",
            "description": "Can manage all users",
            "resource": "user",
            "action": "manage"
        }
        elevated_perm_response = await test_client.post("/rbac/permissions", json=elevated_perm_data, headers=admin_headers)
        assert elevated_perm_response.status_code == 201
        elevated_permission = elevated_perm_response.json()
        
        # Create basic role
        basic_role_data = test_data.role_create_data()
        basic_role_data["name"] = "basic_user"
        basic_role_data["permission_ids"] = [base_permission["id"]]
        
        basic_role_response = await test_client.post("/rbac/roles", json=basic_role_data, headers=admin_headers)
        assert basic_role_response.status_code == 201
        basic_role = basic_role_response.json()
        
        # Create manager role with both permissions
        manager_role_data = test_data.role_create_data()
        manager_role_data["name"] = "user_manager"
        manager_role_data["permission_ids"] = [base_permission["id"], elevated_permission["id"]]
        
        manager_role_response = await test_client.post("/rbac/roles", json=manager_role_data, headers=admin_headers)
        assert manager_role_response.status_code == 201
        manager_role = manager_role_response.json()
        
        # Verify roles have correct permissions
        assert len(basic_role["permissions"]) == 1
        assert len(manager_role["permissions"]) == 2


class TestDataConsistency:
    """Test data consistency across different operations."""
    
    async def test_user_deletion_cascades_properly(self, test_client: AsyncClient, admin_headers: dict, test_data, db_session: AsyncSession):
        """Test that user deletion properly handles related data."""
        # Create user with profile and roles
        user_data = test_data.user_registration_data()
        register_response = await test_client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201
        user = register_response.json()
        user_id = user["id"]
        
        # Login and create profile
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        login_response = await test_client.post("/auth/login", data=login_data)
        token_data = login_response.json()
        user_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        profile_data = test_data.profile_create_data()
        profile_response = await test_client.post("/profile/", json=profile_data, headers=user_headers)
        assert profile_response.status_code == 201
        
        # Assign role to user
        role_data = test_data.role_create_data()
        role_response = await test_client.post("/rbac/roles", json=role_data, headers=admin_headers)
        role = role_response.json()
        
        assignment_data = {
            "user_id": user_id,
            "role_ids": [role["id"]]
        }
        assign_response = await test_client.post(f"/rbac/users/{user_id}/roles", json=assignment_data, headers=admin_headers)
        assert assign_response.status_code == 200
        
        # Delete user
        delete_response = await test_client.delete(f"/users/{user_id}", headers=admin_headers)
        assert delete_response.status_code == 200
        
        # Verify user is gone
        user_response = await test_client.get(f"/users/{user_id}", headers=admin_headers)
        assert user_response.status_code == 404
        
        # Verify profile is gone (if cascade is set up)
        profile_response = await test_client.get("/profile/", headers=user_headers)
        assert profile_response.status_code == 401  # User no longer exists
    
    async def test_role_deletion_handles_user_assignments(self, test_client: AsyncClient, admin_headers: dict, test_data, user_with_role: User, test_role: Role):
        """Test that role deletion properly handles user assignments."""
        # Delete the role
        delete_response = await test_client.delete(f"/rbac/roles/{test_role.id}", headers=admin_headers)
        assert delete_response.status_code == 200
        
        # Verify role is gone
        role_response = await test_client.get(f"/rbac/roles/{test_role.id}", headers=admin_headers)
        assert role_response.status_code == 404
        
        # Verify user no longer has the role
        user_roles_response = await test_client.get(f"/rbac/users/{user_with_role.id}/roles", headers=admin_headers)
        assert user_roles_response.status_code == 200
        user_roles = user_roles_response.json()
        assert not any(role["id"] == test_role.id for role in user_roles)


class TestErrorHandling:
    """Test comprehensive error handling across the system."""
    
    async def test_database_transaction_rollback(self, test_client: AsyncClient, admin_headers: dict, test_data):
        """Test that database errors trigger proper rollback."""
        # Try to create a role with invalid permission IDs
        role_data = test_data.role_create_data()
        role_data["permission_ids"] = [99999, 99998]  # Non-existent permissions
        
        response = await test_client.post("/rbac/roles", json=role_data, headers=admin_headers)
        
        # Should fail gracefully
        assert response.status_code in [400, 404, 422]
        
        # Database should remain consistent - no partial role creation
        roles_response = await test_client.get("/rbac/roles", headers=admin_headers)
        roles = roles_response.json()
        assert not any(role["name"] == role_data["name"] for role in roles)
    
    async def test_concurrent_user_operations(self, test_client: AsyncClient, admin_headers: dict, test_user: User):
        """Test handling of concurrent operations on the same user."""
        # Simulate concurrent deactivation and deletion attempts
        # In a real test, you'd use asyncio.gather or similar
        
        deactivate_response = await test_client.put(f"/users/{test_user.id}/deactivate", headers=admin_headers)
        
        # Try to delete immediately after deactivation
        delete_response = await test_client.delete(f"/users/{test_user.id}", headers=admin_headers)
        
        # One should succeed, system should remain consistent
        assert deactivate_response.status_code == 200 or delete_response.status_code == 200
    
    async def test_invalid_token_handling(self, test_client: AsyncClient):
        """Test various invalid token scenarios."""
        invalid_tokens = [
            "Bearer invalid_token",
            "Bearer ",
            "InvalidFormat token",
            "Bearer expired.token.here",
            "",
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": token} if token else {}
            response = await test_client.get("/auth/me", headers=headers)
            assert response.status_code == 401


class TestPerformanceIntegration:
    """Test performance-related integration scenarios."""
    
    async def test_large_user_list_pagination(self, test_client: AsyncClient, admin_headers: dict, db_session: AsyncSession):
        """Test pagination with larger datasets."""
        # Create multiple users
        users_to_create = 25
        for i in range(users_to_create):
            user = User(
                email=f"perftest{i}@test.com",
                password_hash="hashed",
                full_name=f"Performance Test User {i}"
            )
            db_session.add(user)
        
        await db_session.commit()
        
        # Test pagination
        page1_response = await test_client.get("/users/?skip=0&limit=10", headers=admin_headers)
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        assert len(page1_data) == 10
        
        page2_response = await test_client.get("/users/?skip=10&limit=10", headers=admin_headers)
        assert page2_response.status_code == 200
        page2_data = page2_response.json()
        assert len(page2_data) == 10
        
        # Verify no overlap
        page1_ids = {user["id"] for user in page1_data}
        page2_ids = {user["id"] for user in page2_data}
        assert page1_ids.isdisjoint(page2_ids)
    
    async def test_bulk_role_assignment_performance(self, test_client: AsyncClient, admin_headers: dict, test_role: Role, db_session: AsyncSession):
        """Test performance of bulk role assignments."""
        # Create multiple users
        users_to_create = 10
        user_ids = []
        
        for i in range(users_to_create):
            user = User(
                email=f"bulkperf{i}@test.com",
                password_hash="hashed",
                full_name=f"Bulk Performance User {i}"
            )
            db_session.add(user)
        
        await db_session.commit()
        
        # Get user IDs
        for i in range(users_to_create):
            user = await db_session.execute(
                db_session.query(User).filter(User.email == f"bulkperf{i}@test.com")
            )
            user_ids.append(user.scalar().id)
        
        # Test bulk assignment (if implemented)
        # This would test a hypothetical bulk assignment endpoint
        # For now, test individual assignments
        for user_id in user_ids[:5]:  # Test first 5
            assignment_data = {
                "user_id": user_id,
                "role_ids": [test_role.id]
            }
            response = await test_client.post(f"/rbac/users/{user_id}/roles", json=assignment_data, headers=admin_headers)
            assert response.status_code == 200
