"""
pytest configuration and fixtures for the Users API testing suite.

This module provides:
- Test database setup and teardown
- Authentication fixtures
- Test client configuration  
- Common test data factories
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base, get_db_session
from app.models import User
from app.rbac_models import Role, Permission
from app.auth import get_password_hash, create_access_token


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
        echo=False,  # Set to True for SQL debugging
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function") 
async def test_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with dependency overrides."""
    
    # Override the database dependency
    def override_get_db_session():
        return db_session
    
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    # Create test client
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user."""
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("adminpass123"),
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def inactive_user(db_session: AsyncSession) -> User:
    """Create an inactive user."""
    user = User(
        email="inactive@example.com",
        username="inactive",
        hashed_password=get_password_hash("password123"),
        is_active=False,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def user_token(test_user: User) -> str:
    """Create a JWT token for test user."""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Create a JWT token for admin user."""
    return create_access_token(data={"sub": admin_user.email})


@pytest.fixture
def auth_headers(user_token: str) -> dict:
    """Create authorization headers for test user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Create authorization headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture
async def test_permission(db_session: AsyncSession) -> Permission:
    """Create a test permission."""
    permission = Permission(
        name="test:read",
        description="Test read permission",
        resource="test",
        action="read"
    )
    db_session.add(permission)
    await db_session.commit()
    await db_session.refresh(permission)
    return permission


@pytest_asyncio.fixture
async def test_role(db_session: AsyncSession, test_permission: Permission) -> Role:
    """Create a test role with permission."""
    role = Role(
        name="test_role",
        description="Test role",
        is_default=False,
        is_system=False
    )
    db_session.add(role)
    await db_session.flush()
    
    # Add permission to role
    role.permissions = [test_permission]
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest.fixture
async def user_with_role(test_user: User, test_role: Role, db_session: AsyncSession) -> User:
    """Create a user with assigned role."""
    test_user.roles.append(test_role)
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user


@pytest.fixture
def test_data():
    """Provides test data factory methods."""
    
    class TestDataFactory:
        def user_registration_data(self):
            """Generate user registration data."""
            import random
            import string
            
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            return {
                "email": f"testuser_{random_suffix}@example.com",
                "password": "SecurePass123!",
                "full_name": f"Test User {random_suffix}",
                "username": f"testuser_{random_suffix}"
            }
        
        def profile_create_data(self):
            """Generate profile creation data."""
            return {
                "bio": "This is a test bio for the user profile.",
                "location": "Test City, Test Country",
                "website": "https://testuser.example.com",
                "birth_date": "1990-01-01",
                "phone_number": "+1234567890"
            }
        
        def permission_create_data(self):
            """Generate permission creation data."""
            import random
            import string
            
            random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
            return {
                "name": f"test_permission_{random_suffix}",
                "description": f"Test permission for {random_suffix}",
                "resource": f"test_resource_{random_suffix}",
                "action": "read"
            }
        
        def role_create_data(self, permission_ids=None):
            """Generate role creation data."""
            import random
            import string
            
            random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
            return {
                "name": f"test_role_{random_suffix}",
                "description": f"Test role for {random_suffix}",
                "is_default": False,
                "permission_ids": permission_ids or []
            }
    
    return TestDataFactory()


# Test data factories
class TestData:
    """Factory for creating test data."""
    
    @staticmethod
    def user_create_data(**kwargs):
        """Create user registration data."""
        default_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpass123",
            "is_active": True
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def user_update_data(**kwargs):
        """Create user update data."""
        default_data = {
            "username": "updateduser",
            "email": "updated@example.com"
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def profile_update_data(**kwargs):
        """Create profile update data."""
        default_data = {
            "bio": "Updated bio",
            "location": "Updated City",
            "website": "https://updated.example.com"
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def permission_create_data(**kwargs):
        """Create permission data."""
        default_data = {
            "name": "test:write",
            "description": "Test write permission",
            "resource": "test",
            "action": "write"
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def role_create_data(**kwargs):
        """Create role data."""
        default_data = {
            "name": "test_new_role",
            "description": "New test role",
            "is_default": False,
            "permission_ids": []
        }
        default_data.update(kwargs)
        return default_data


# Make TestData available as a fixture
@pytest.fixture
def test_data():
    """Provide access to test data factory."""
    return TestData
