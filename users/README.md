# Users Microservice Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Application Layer](#application-layer)
5. [Database Layer](#database-layer)
6. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
7. [Comprehensive Testing Suite](#comprehensive-testing-suite)
8. [Database Migrations](#database-migrations)
9. [Containerization](#containerization)
10. [Kubernetes Configuration](#kubernetes-configuration)
11. [Development Workflow](#development-workflow)
12. [API Endpoints](#api-endpoints)
13. [Best Practices Demonstrated](#best-practices-demonstrated)

## Overview

This is a modern FastAPI-based microservice that demonstrates production-ready practices for building, containerizing, and deploying applications on Kubernetes. The service provides comprehensive user management functionality with authentication, role-based access control (RBAC), user profiles, and PostgreSQL persistence.

### Key Technologies
- **FastAPI**: Modern, fast Python web framework
- **SQLAlchemy 2.0**: Modern Python SQL toolkit with async support
- **PostgreSQL**: Production-ready relational database
- **JWT Authentication**: Secure token-based authentication
- **RBAC System**: Role-Based Access Control with permissions
- **Alembic**: Database migration management
- **pytest**: Comprehensive testing framework with async support
- **Docker**: Containerization platform
- **Kubernetes**: Container orchestration
- **Skaffold**: Development workflow tool

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                      │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST API + JWT Authentication
┌─────────────────────▼───────────────────────────────────────┐
│                  Load Balancer                             │
│                 (Kubernetes Service)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Users API Pod                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              FastAPI Application                    │   │
│  │  ┌─────────┬─────────┬─────────┬─────────────────┐   │   │
│  │  │  Auth   │  Users  │ Profile │      RBAC       │   │   │
│  │  │(JWT/Reg)│ (CRUD)  │ (Mgmt)  │(Roles/Perms)    │   │   │
│  │  └─────────┴─────────┴─────────┴─────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │     Models, Schemas & Validation Layer         │   │   │
│  │  │  • User Models    • RBAC Models                │   │   │
│  │  │  • Pydantic Schemas • JWT Auth                 │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │           Database Connection Pool              │   │   │
│  │  │        • Async SQLAlchemy 2.0                  │   │   │
│  │  │        • Connection Health Checks              │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┐   │
└─────────────────────┬───────────────────────────────────────┘
                      │ SQL Connection
┌─────────────────────▼───────────────────────────────────────┐
│                PostgreSQL StatefulSet                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Database                            │   │
│  │    ┌────────────────┬─────────────────────────────┐ │   │
│  │    │   users table  │      RBAC Tables            │ │   │
│  │    │  - id (PK)     │  • permissions              │ │   │
│  │    │  - email       │  • roles                    │ │   │
│  │    │  - full_name   │  • role_permissions         │ │   │
│  │    │  - password    │  • user_roles               │ │   │
│  │    │  - is_active   │                             │ │   │
│  │    │  - is_admin    │                             │ │   │
│  │    │  - bio         │                             │ │   │
│  │    │  - avatar_url  │                             │ │   │
│  │    │  - preferences │                             │ │   │
│  │    │  - timestamps  │                             │ │   │
│  │    └────────────────┴─────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
users/
├── app/                          # Application source code
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── auth.py                  # Authentication utilities (JWT, password hashing)
│   ├── db.py                    # Database configuration and sessions
│   ├── models.py                # SQLAlchemy user models
│   ├── schemas.py               # Pydantic data validation schemas
│   ├── rbac_models.py           # RBAC database models (roles, permissions)
│   ├── rbac_schemas.py          # RBAC Pydantic schemas
│   ├── rbac_auth.py             # RBAC authentication decorators
│   └── routers/                 # API route handlers
│       ├── __init__.py
│       ├── auth.py             # Authentication endpoints (login, register)
│       ├── users.py            # User management endpoints (admin)
│       ├── profile.py          # User profile management endpoints
│       └── rbac.py             # RBAC management endpoints (admin)
├── alembic/                     # Database migration system
│   ├── env.py                  # Alembic environment configuration
│   ├── script.py.mako          # Migration script template
│   └── versions/               # Migration version files
│       ├── 001_initial_migration.py
│       ├── 002_add_user_profile_fields.py
│       └── 003_add_rbac_tables.py
├── tests/                       # Comprehensive test suite
│   ├── conftest.py             # pytest configuration and fixtures
│   ├── test_auth.py            # Authentication endpoint tests
│   ├── test_users.py           # User management tests
│   ├── test_profile.py         # Profile management tests
│   ├── test_rbac.py            # RBAC system tests
│   └── test_integration.py     # End-to-end integration tests
├── k8s/                         # Kubernetes manifests
│   ├── app-db.secret.yaml      # Database credentials and JWT secret
│   ├── postgres.service.yaml   # PostgreSQL service discovery
│   ├── postgres.statefulset.yaml # PostgreSQL deployment
│   ├── migration.job.yaml      # Database migration job
│   ├── users-api.deployment.yaml # Application deployment
│   └── users-api.service.yaml  # Application service discovery
├── Dockerfile                   # Container image definition
├── .dockerignore               # Files to exclude from Docker build
├── requirements.txt            # Python dependencies
├── pytest.ini                 # pytest configuration
├── alembic.ini                # Alembic configuration
├── run_tests.py               # Comprehensive test runner script
├── setup_rbac.py              # RBAC system setup script
├── migrate.py                 # Database migration helper
├── skaffold.yaml              # Development workflow configuration
├── demo_api.py                # Comprehensive API demonstration script
└── README.md                  # This documentation file
```

## Application Layer

### 1. FastAPI Application (`app/main.py`)

The main application file demonstrates modern Python async patterns and proper application lifecycle management:

```python
from fastapi import FastAPI, HTTPException, Depends
import os
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .db import engine, Base, get_session
from .routers import users as users_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables at startup (we'll switch to Alembic migrations later)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="Users API", version="0.2.0", lifespan=lifespan)
```

**Key Learning Points:**
- **Lifespan Management**: The `lifespan` context manager handles startup and shutdown events
- **Async Context Manager**: Proper resource management using `async with`
- **Database Initialization**: Tables are created automatically on startup
- **Clean Shutdown**: Database connections are properly disposed of

### 2. Health Check Endpoints

Essential for Kubernetes deployments:

```python
@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.get("/readyz")
async def ready():
    try:
        async with get_session() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="db not ready")
```

**Why This Matters:**
- **Liveness Probe** (`/healthz`): Kubernetes uses this to determine if the pod is alive
- **Readiness Probe** (`/readyz`): Kubernetes uses this to determine if the pod can accept traffic
- **Database Connectivity**: Readiness check verifies database connection

### 3. Modular Router System (`app/routers/users.py`)

FastAPI's router system promotes clean, modular code:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db_session
from .. import models
from ..schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_db_session)):
    res = await session.execute(select(models.User).order_by(models.User.id))
    return [UserRead.model_validate(u) for u in res.scalars().all()]
```

**Architecture Benefits:**
- **Separation of Concerns**: Each router handles a specific domain
- **Dependency Injection**: Database sessions are injected automatically
- **Type Safety**: Response models ensure consistent API contracts

## Database Layer

### 1. Database Configuration (`app/db.py`)

Modern async SQLAlchemy setup with proper connection management:

```python
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://appuser:apppass@postgres:5432/appdb",
)

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
```

**Key Features:**
- **Environment Configuration**: Database URL from environment variables
- **Connection Pooling**: Built-in connection pool with health checks
- **Async Support**: Full async/await support for better performance

### 2. Database Models (`app/models.py`)

Modern SQLAlchemy 2.0 syntax with type hints:

```python
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class User(Base):
    __tablename__ = "users"

    # Basic user information
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Extended profile fields
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    # User preferences stored as JSON
    preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    
    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
```

**Modern Patterns:**
- **Type Annotations**: `Mapped[]` provides better IDE support and type checking
- **Timezone Awareness**: Proper UTC timestamp handling
- **Database Constraints**: Unique constraints and indexes for performance

### 3. Data Validation (`app/schemas.py`)

Pydantic schemas for request/response validation:

```python
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = None

class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
```

**Benefits:**
- **Automatic Validation**: Email format validation, type checking
- **API Documentation**: Schemas generate OpenAPI documentation
- **Serialization**: Automatic conversion between database models and JSON

## Role-Based Access Control (RBAC)

The microservice implements a comprehensive RBAC system that provides fine-grained access control through roles and permissions.

### RBAC Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RBAC System Architecture                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                     Users                                   │
│  • Can have multiple roles                                  │
│  • Inherit permissions from roles                           │
│  • Can be admin (superuser)                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │ Many-to-Many
┌─────────────────────▼───────────────────────────────────────┐
│                     Roles                                   │
│  • Named role (e.g., "editor", "moderator")                │
│  • Can be default role for new users                       │
│  • Can have multiple permissions                            │
│  • Can be assigned to multiple users                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ Many-to-Many
┌─────────────────────▼───────────────────────────────────────┐
│                  Permissions                                │
│  • Resource-based (e.g., "user", "post", "admin")         │
│  • Action-based (e.g., "read", "write", "delete")         │
│  • Hierarchical support (admin:all grants everything)      │
└─────────────────────────────────────────────────────────────┘
```

### RBAC Models (`app/rbac_models.py`)

```python
from sqlalchemy import String, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

# Association table for many-to-many relationship between roles and permissions
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    mapped_column('role_id', ForeignKey('roles.id'), primary_key=True),
    mapped_column('permission_id', ForeignKey('permissions.id'), primary_key=True)
)

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    mapped_column('user_id', ForeignKey('users.id'), primary_key=True),
    mapped_column('role_id', ForeignKey('roles.id'), primary_key=True)
)

class Permission(Base):
    __tablename__ = "permissions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permissions, back_populates="permissions"
    )
    
    def __str__(self) -> str:
        return f"{self.resource}:{self.action}"

class Role(Base):
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permissions, back_populates="roles"
    )
    users: Mapped[list["User"]] = relationship(
        secondary=user_roles, back_populates="roles"
    )
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if role has specific permission."""
        # Admin role has all permissions
        if any(p.resource == "admin" and p.action == "all" for p in self.permissions):
            return True
        
        # Check for specific permission
        return any(
            p.resource == resource and p.action == action 
            for p in self.permissions
        )
```

### RBAC Authentication (`app/rbac_auth.py`)

```python
from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .auth import get_current_user
from .models import User
from .db import get_db_session

def require_permission(resource: str, action: str):
    """Decorator to require specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user and session from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has permission
            if not current_user.has_permission(resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {resource}:{action}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin(func):
    """Decorator to require admin privileges."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user or not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator privileges required"
            )
        return await func(*args, **kwargs)
    return wrapper

def require_role(role_name: str):
    """Decorator to require specific role."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user or not current_user.has_role(role_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role_name}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### RBAC Endpoints (`app/routers/rbac.py`)

The RBAC router provides comprehensive management endpoints:

```python
# Permission Management
POST /rbac/permissions          # Create permission (admin only)
GET /rbac/permissions           # List all permissions (admin only)
DELETE /rbac/permissions/{id}   # Delete permission (admin only)

# Role Management
POST /rbac/roles               # Create role (admin only)
GET /rbac/roles                # List all roles (admin only)
GET /rbac/roles/{id}           # Get specific role (admin only)
PUT /rbac/roles/{id}           # Update role (admin only)
DELETE /rbac/roles/{id}        # Delete role (admin only)

# User Role Assignment
POST /rbac/users/{user_id}/roles    # Assign roles to user (admin only)
GET /rbac/users/{user_id}/roles     # Get user's roles (admin only)
GET /rbac/users                     # List users with their roles (admin only)

# Permission Checking
POST /rbac/check-permission         # Check if user has permission (admin only)
```

### RBAC Setup Script (`setup_rbac.py`)

```bash
# Initialize RBAC system with default roles and permissions
python setup_rbac.py
```

This script creates:
- Basic permissions (user:read, user:write, admin:all)
- Default roles (user, moderator, admin)
- Assigns permissions to roles appropriately

## Comprehensive Testing Suite

The microservice includes a robust testing framework using pytest with comprehensive coverage across all functionality areas.

### Testing Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Testing Strategy                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Unit Tests                                 │
│  • Individual component testing                             │
│  • Mocked dependencies                                      │
│  • Fast execution                                          │
│  • High code coverage                                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│               Integration Tests                             │
│  • End-to-end workflow testing                             │
│  • Real database interactions                              │
│  • Cross-component validation                              │
│  • Production-like scenarios                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Security Tests                               │
│  • Authentication validation                               │
│  • Authorization enforcement                               │
│  • Input sanitization                                      │
│  • RBAC compliance                                         │
└─────────────────────────────────────────────────────────────┘
```

### Test Structure

```
tests/
├── conftest.py              # pytest configuration and fixtures
│   ├── Database setup (test database, session management)
│   ├── User fixtures (test users, admin users, authenticated clients)
│   ├── RBAC fixtures (roles, permissions, user assignments)
│   └── Test data factories (generate test data)
├── test_auth.py             # Authentication system tests
│   ├── User registration validation
│   ├── Login/logout workflows
│   ├── Token generation and validation
│   ├── Password security tests
│   └── Authentication error handling
├── test_users.py            # User management tests
│   ├── User CRUD operations
│   ├── User status management (activate/deactivate)
│   ├── Admin user operations
│   ├── User search and filtering
│   └── Bulk user operations
├── test_profile.py          # Profile management tests
│   ├── Profile creation and updates
│   ├── Preferences management
│   ├── Avatar handling
│   ├── Privacy settings
│   └── Profile validation
├── test_rbac.py             # RBAC system tests
│   ├── Permission management
│   ├── Role management
│   ├── User role assignments
│   ├── Permission checking
│   ├── Access control enforcement
│   └── RBAC model logic
└── test_integration.py      # Integration and end-to-end tests
    ├── Complete user workflows
    ├── Authentication + authorization flows
    ├── RBAC + profile interactions
    ├── Data consistency tests
    ├── Error handling scenarios
    └── Performance tests
```

### Test Fixtures (`tests/conftest.py`)

The test configuration provides comprehensive fixtures for testing:

```python
@pytest.fixture(scope="session")
async def test_db_engine():
    """Create test database engine."""
    DATABASE_URL = "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def test_client(test_db_engine) -> AsyncClient:
    """Create test client with database override."""
    async def override_get_db():
        async with AsyncSession(test_db_engine) as session:
            yield session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        password_hash=get_password_hash("testpass123"),
        full_name="Test User",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin test user."""
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("adminpass123"),
        full_name="Admin User",
        is_active=True,
        is_admin=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin

@pytest.fixture
async def auth_headers(test_client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers for test user."""
    login_data = {"username": test_user.email, "password": "testpass123"}
    response = await test_client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def admin_headers(test_client: AsyncClient, admin_user: User) -> dict:
    """Get authentication headers for admin user."""
    login_data = {"username": admin_user.email, "password": "adminpass123"}
    response = await test_client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Test Runner Script (`run_tests.py`)

The test runner provides multiple testing modes:

```bash
# Run all tests with coverage
python run_tests.py --all

# Run specific test categories
python run_tests.py --unit                # Unit tests only
python run_tests.py --integration         # Integration tests only
python run_tests.py --auth                # Authentication tests
python run_tests.py --rbac                # RBAC tests
python run_tests.py --profile             # Profile tests
python run_tests.py --security            # Security tests

# Run tests with specific options
python run_tests.py --unit -v             # Verbose unit tests
python run_tests.py --all --no-coverage   # All tests without coverage
python run_tests.py -k "test_login"       # Tests matching keyword

# Utility commands
python run_tests.py --setup-db            # Set up test database
python run_tests.py --coverage-report     # Generate coverage report
python run_tests.py --clean               # Clean test artifacts
python run_tests.py --lint                # Run code quality checks
```

### Test Configuration (`pytest.ini`)

```ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    --strict-markers
    --strict-config
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
testpaths = tests
python_files = test_*.py
asyncio_mode = auto
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    auth: marks tests related to authentication
    rbac: marks tests related to RBAC
    profile: marks tests related to user profiles
    security: marks tests related to security features
```

### Test Examples

**Authentication Test:**
```python
async def test_user_registration_and_login(test_client: AsyncClient, test_data):
    """Test complete registration and login flow."""
    # Register new user
    user_data = test_data.user_registration_data()
    register_response = await test_client.post("/auth/register", json=user_data)
    
    assert register_response.status_code == 201
    user = register_response.json()
    
    # Login with new user
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    login_response = await test_client.post("/auth/login", data=login_data)
    
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
```

**RBAC Test:**
```python
async def test_role_based_access_control(test_client: AsyncClient, admin_headers: dict, auth_headers: dict):
    """Test that RBAC properly restricts access."""
    # Admin should access admin endpoints
    admin_response = await test_client.get("/rbac/permissions", headers=admin_headers)
    assert admin_response.status_code == 200
    
    # Regular user should be denied
    user_response = await test_client.get("/rbac/permissions", headers=auth_headers)
    assert user_response.status_code == 403
```

**Integration Test:**
```python
async def test_complete_user_workflow(test_client: AsyncClient, test_data):
    """Test complete user workflow from registration to profile management."""
    # 1. Register user
    user_data = test_data.user_registration_data()
    register_response = await test_client.post("/auth/register", json=user_data)
    assert register_response.status_code == 201
    
    # 2. Login
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    login_response = await test_client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create profile
    profile_data = test_data.profile_create_data()
    profile_response = await test_client.post("/profile/", json=profile_data, headers=headers)
    assert profile_response.status_code == 201
    
    # 4. Update preferences
    preferences = {"theme": "dark", "notifications": True}
    prefs_response = await test_client.put("/profile/preferences", json=preferences, headers=headers)
    assert prefs_response.status_code == 200
    
    # 5. Verify complete profile
    final_response = await test_client.get("/profile/", headers=headers)
    assert final_response.status_code == 200
    final_profile = final_response.json()
    assert final_profile["bio"] == profile_data["bio"]
    assert final_profile["preferences"]["theme"] == "dark"
```

### Running Tests

```bash
# Basic test run
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run tests with specific marker
pytest -m auth

# Run tests matching keyword
pytest -k "test_login"

# Run with verbose output
pytest -v

# Run using the test runner script
python run_tests.py --all -v
```

### Coverage Reports

The testing suite generates comprehensive coverage reports:

- **Terminal Report**: Shows coverage percentages in the terminal
- **HTML Report**: Generates detailed HTML coverage report in `htmlcov/`
- **XML Report**: Generates XML coverage report for CI/CD integration

```bash
# Generate and view HTML coverage report
python run_tests.py --coverage-report
open htmlcov/index.html
```

## Database Migrations

The microservice uses Alembic for database schema management and versioning.

### Migration System

```
alembic/
├── env.py                      # Alembic environment configuration
├── script.py.mako             # Migration script template
└── versions/                   # Migration version files
    ├── 001_initial_migration.py        # Initial user tables
    ├── 002_add_user_profile_fields.py  # Extended user profile
    └── 003_add_rbac_tables.py          # RBAC system tables
```

### Migration Commands

```bash
# Generate new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current migration status
alembic current

# View migration history
alembic history

# Use migration helper script
python migrate.py upgrade        # Apply all pending migrations
python migrate.py current       # Show current migration
python migrate.py history       # Show migration history
```

### Migration Files

**Initial Migration (001):**
```python
def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
```

**RBAC Migration (003):**
```python
def upgrade() -> None:
    # Create permissions table
    op.create_table('permissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('resource', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create roles table
    op.create_table('roles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create association tables
    op.create_table('role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    
    op.create_table('user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
```

## Containerization

### Multi-Stage Dockerfile

Our Dockerfile demonstrates production best practices:

```dockerfile
# syntax=docker/dockerfile:1.7

# --- builder stage ---
FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /workspace
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN python -m venv /venv && /venv/bin/pip install --no-cache-dir \
    -r requirements.txt

# --- runtime stage ---
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    PORT=8000 \
    APP_ENV=dev \
    PYTHONPATH="/app"
WORKDIR /app
# Create non-root user
RUN useradd -u 10001 -s /usr/sbin/nologin appuser && \
    mkdir -p /app && chown -R appuser:appuser /app
COPY --from=builder /venv /venv
COPY . /app
RUN python -c "import os, sys, importlib; print('sys.path=', sys.path); \
    importlib.import_module('app'); \
    print(\"Imported 'app' OK, contents:\", os.listdir('/app/app'))"
USER 10001:10001

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Security & Performance Features:**
- **Multi-stage Build**: Smaller final image, build tools not included in runtime
- **Non-root User**: Security best practice, runs with limited privileges
- **Layer Optimization**: Dependencies installed separately for better caching
- **Import Verification**: Ensures the application can be imported successfully

## Kubernetes Configuration

### 1. Database Secret (`k8s/app-db.secret.yaml`)

Secure credential management:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-db-secret
type: Opaque
stringData:
  POSTGRES_USER: appuser
  POSTGRES_PASSWORD: apppass
  POSTGRES_DB: appdb
  DATABASE_URL: postgresql+asyncpg://appuser:apppass@postgres:5432/appdb
```

**Security Notes:**
- In production, use external secret management (e.g., Vault, AWS Secrets Manager)
- Never commit real secrets to version control
- Use `stringData` for base64 encoding automation

### 2. PostgreSQL StatefulSet (`k8s/postgres.statefulset.yaml`)

Stateful database deployment:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  template:
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          envFrom:
            - secretRef:
                name: app-db-secret
          volumeMounts:
            - name: pgdata
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: pgdata
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi
```

**StatefulSet Benefits:**
- **Persistent Storage**: Data survives pod restarts
- **Stable Network Identity**: Consistent hostname for database connections
- **Ordered Deployment**: Ensures proper startup sequence

### 3. Application Deployment (`k8s/users-api.deployment.yaml`)

Stateless application deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: users-api
spec:
  replicas: 1
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
      containers:
        - name: users-api
          image: users-api
          ports:
            - containerPort: 8000
              name: http
          envFrom:
            - secretRef:
                name: app-db-secret
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            initialDelaySeconds: 3
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
          resources:
            requests:
              cpu: "50m"
              memory: "64Mi"
            limits:
              cpu: "250m"
              memory: "128Mi"
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
```

**Production Features:**
- **Security Context**: Non-root user, read-only filesystem
- **Health Probes**: Automatic health monitoring
- **Resource Limits**: Prevents resource exhaustion
- **Environment Injection**: Configuration via secrets

### 4. Service Discovery (`k8s/users-api.service.yaml`)

Network abstraction layer:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: users-api
spec:
  type: ClusterIP
  selector:
    app: users-api
  ports:
    - name: http
      port: 8000
      targetPort: http
```

**Service Benefits:**
- **Load Balancing**: Automatic traffic distribution
- **Service Discovery**: Stable DNS name for the application
- **Port Abstraction**: Decouples external and internal ports

## Development Workflow

### Skaffold Configuration (`skaffold.yaml`)

Development workflow automation:

```yaml
apiVersion: skaffold/v4beta11
kind: Config
metadata:
  name: users-api
build:
  local:
    push: false
  artifacts:
    - image: users-api
      context: .
      docker:
        dockerfile: Dockerfile
deploy:
  kubectl:
    manifests:
      - k8s/*.yaml
portForward:
  - resourceType: service
    resourceName: users-api
    port: 8000
    localPort: 8000
```

**Workflow Features:**
- **Hot Reload**: Automatic rebuilds on code changes
- **Local Development**: No need to push to remote registries
- **Port Forwarding**: Easy access to services running in cluster

### Development Commands

```bash
# Start development environment
cd users/
skaffold dev --port-forward

# The above command will:
# 1. Build the Docker image
# 2. Deploy to Kubernetes
# 3. Set up port forwarding
# 4. Watch for file changes
# 5. Automatically rebuild and redeploy on changes
```

## API Endpoints

### Available Endpoints

1. **Health Check**
   ```
   GET / - Basic service information
   GET /healthz - Liveness probe
   GET /readyz - Readiness probe (includes DB check)
   ```

2. **Authentication**
   ```
   POST /auth/register - Register a new user
   POST /auth/login - Login and get access token
   GET /auth/me - Get current user information
   POST /auth/test-token - Test access token validity
   POST /auth/refresh - Refresh access token
   POST /auth/logout - Logout and invalidate token
   ```

3. **User Management (Admin only)**
   ```
   GET /users/ - List all users with pagination and filtering
   GET /users/{user_id} - Get specific user by ID
   PUT /users/{user_id}/activate - Activate user account
   PUT /users/{user_id}/deactivate - Deactivate user account
   PUT /users/{user_id}/make-admin - Promote user to admin
   PUT /users/{user_id}/remove-admin - Remove admin privileges
   DELETE /users/{user_id} - Delete user account
   PUT /users/bulk/activate - Bulk activate users
   PUT /users/bulk/deactivate - Bulk deactivate users
   PUT /users/bulk/delete - Bulk delete users
   ```

4. **Profile Management**
   ```
   GET /profile/ - Get current user's complete profile
   POST /profile/ - Create user profile
   PUT /profile/ - Update current user's profile information
   DELETE /profile/ - Delete current user's profile
   GET /profile/preferences - Get current user's preferences
   PUT /profile/preferences - Update current user's preferences
   DELETE /profile/avatar - Remove current user's avatar
   GET /profile/{user_id} - Get another user's public profile (if public)
   ```

5. **Role-Based Access Control (Admin only)**
   ```
   # Permission Management
   POST /rbac/permissions - Create new permission
   GET /rbac/permissions - List all permissions
   GET /rbac/permissions/{id} - Get specific permission
   PUT /rbac/permissions/{id} - Update permission
   DELETE /rbac/permissions/{id} - Delete permission
   
   # Role Management
   POST /rbac/roles - Create new role
   GET /rbac/roles - List all roles
   GET /rbac/roles/{id} - Get specific role with permissions
   PUT /rbac/roles/{id} - Update role and its permissions
   DELETE /rbac/roles/{id} - Delete role
   
   # User Role Assignment
   POST /rbac/users/{user_id}/roles - Assign roles to user
   GET /rbac/users/{user_id}/roles - Get user's assigned roles
   DELETE /rbac/users/{user_id}/roles/{role_id} - Remove role from user
   GET /rbac/users - List all users with their roles
   
   # Permission Checking
   POST /rbac/check-permission - Check if current user has specific permission
   GET /rbac/my-permissions - Get current user's effective permissions
   ```

### Usage Examples

#### Authentication Flow
```bash
# Register a new user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "full_name": "Alice Johnson",
    "password": "SecurePassword123!"
  }'

# Login to get access token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=SecurePassword123!"

# Use the returned access_token in subsequent requests
export TOKEN="your_access_token_here"

# Get current user info
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/auth/me
```

#### Profile Management
```bash
# Create user profile
curl -X POST http://localhost:8000/profile/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "I am a software developer passionate about microservices!",
    "location": "San Francisco, CA",
    "website": "https://alice-dev.com",
    "phone_number": "+1-555-0123",
    "birth_date": "1990-05-15"
  }'

# Update user preferences
curl -X PUT http://localhost:8000/profile/preferences \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "dark",
    "language": "en",
    "timezone": "America/Los_Angeles",
    "notifications_email": true,
    "notifications_sms": false,
    "privacy_public_profile": true
  }'

# Get complete profile
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/profile/
```

#### RBAC Management (Admin only)
```bash
# Create a permission
curl -X POST http://localhost:8000/rbac/permissions \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "manage_posts",
    "description": "Can create, edit, and delete posts",
    "resource": "post",
    "action": "manage"
  }'

# Create a role with permissions
curl -X POST http://localhost:8000/rbac/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "content_editor",
    "description": "Content editors can manage posts and moderate comments",
    "is_default": false,
    "permission_ids": [1, 2, 3]
  }'

# Assign role to user
curl -X POST http://localhost:8000/rbac/users/2/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "role_ids": [1]
  }'

# Check user's permissions
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/rbac/my-permissions

# List all users with their roles (admin only)
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/rbac/users
```

#### User Management (Admin only)
```bash
# List all users with filtering
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8000/users/?skip=0&limit=10&search=alice&active_only=true"

# Deactivate a user
curl -X PUT http://localhost:8000/users/2/deactivate \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Promote user to admin
curl -X PUT http://localhost:8000/users/2/make-admin \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Bulk operations
curl -X PUT http://localhost:8000/users/bulk/deactivate \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [3, 4, 5]
  }'
```

#### Testing Scripts
You can run our comprehensive demo and test scripts:

```bash
# Run the comprehensive API demo script
cd /home/super/Documents/QuizAppFull/users
python demo_api.py

# Run the complete test suite
python run_tests.py --all

# Run specific test categories
python run_tests.py --auth        # Authentication tests
python run_tests.py --rbac        # RBAC tests
python run_tests.py --profile     # Profile tests
python run_tests.py --integration # Integration tests

# Set up RBAC system with default roles and permissions
python setup_rbac.py

# Run database migrations
python migrate.py upgrade
```

### API Documentation

FastAPI automatically generates interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Best Practices Demonstrated

### 1. **Security**
- JWT-based authentication with secure token handling
- Password hashing with bcrypt
- Role-Based Access Control (RBAC) system
- Non-root container execution
- Read-only root filesystem
- Secrets management via Kubernetes secrets
- Input validation and sanitization with Pydantic
- SQL injection prevention through SQLAlchemy ORM
- Permission-based endpoint protection

### 2. **Reliability**
- Health checks for proper Kubernetes orchestration
- Graceful application lifecycle management
- Database connection pooling with health checks
- Comprehensive error handling and logging
- Database transaction management
- Automatic rollback on failures
- Resource limits and requests for stability

### 3. **Testing & Quality Assurance**
- Comprehensive test suite with 80%+ code coverage
- Unit tests for individual components
- Integration tests for end-to-end workflows
- Security tests for authentication and authorization
- Test fixtures and factories for data generation
- Automated test runner with multiple modes
- Mock-based testing for external dependencies
- Performance and load testing capabilities

### 4. **Database Management**
- Async SQLAlchemy 2.0 with modern patterns
- Database migrations with Alembic
- Version-controlled schema changes
- Proper foreign key relationships
- Audit timestamps on all models
- Database indexing for performance
- Connection pooling and health monitoring

### 5. **Observability**
- Structured logging with uvicorn
- Health endpoints for monitoring (/healthz, /readyz)
- Clear error messages and HTTP status codes
- Request/response logging
- Database query logging (configurable)
- Performance metrics collection points

### 6. **Scalability**
- Stateless application design
- Async/await for better concurrency
- Connection pooling for database efficiency
- Horizontal scaling ready (increase replicas)
- Efficient pagination for large datasets
- Bulk operations for administrative tasks
- Caching strategies for frequently accessed data

### 7. **Maintainability**
- Modular code structure with clear separation of concerns
- Type hints throughout the codebase
- Comprehensive documentation
- Consistent naming conventions
- Pydantic schemas for data validation
- Router-based endpoint organization
- Configuration management via environment variables

### 8. **Development Experience**
- Hot reload with Skaffold for rapid development
- Automatic API documentation with FastAPI
- Local development on Kubernetes
- Easy testing with comprehensive test scripts
- Database migration automation
- RBAC setup scripts for quick initialization
- Development-friendly error messages

### 9. **Production Readiness**
- Multi-stage Docker builds for smaller images
- Security contexts and non-privileged execution
- Resource management and limits
- Proper secret handling
- Database migration automation
- Health checks for zero-downtime deployments
- Graceful shutdown handling

### 10. **Modern Python Practices**
- Python 3.12+ features
- Type annotations with Mapped[] syntax
- Context managers for resource management
- Async/await throughout the application
- Pydantic v2 for data validation
- SQLAlchemy 2.0 modern patterns
- pytest with async support

## Next Steps

This foundation supports adding:

1. **Advanced Authentication**
   - OAuth2 integration (Google, GitHub, etc.)
   - Multi-factor authentication (MFA)
   - Session management
   - Password reset workflows

2. **Enhanced RBAC**
   - Hierarchical permissions
   - Resource-level permissions
   - Dynamic permission evaluation
   - Audit logging for access control

3. **Advanced Database Features**
   - Database replication and read replicas
   - Advanced indexing strategies
   - Database partitioning for large datasets
   - Change data capture (CDC)

4. **Production Monitoring**
   - Prometheus metrics integration
   - Distributed tracing with OpenTelemetry
   - Centralized logging with ELK stack
   - Application performance monitoring (APM)

5. **API Enhancement**
   - Rate limiting and throttling
   - API versioning strategies
   - GraphQL endpoint
   - Webhook support

6. **Security Enhancements**
   - API key authentication
   - IP whitelisting/blacklisting
   - Request signing
   - Certificate-based authentication

7. **Performance Optimization**
   - Redis caching layer
   - Database query optimization
   - CDN integration for static assets
   - Background job processing

8. **Advanced Testing**
   - Contract testing with Pact
   - Load testing with Locust
   - Chaos engineering
   - Security penetration testing

This microservice demonstrates a solid, production-ready foundation for building scalable applications on Kubernetes while following modern development practices, comprehensive testing strategies, and enterprise-grade security patterns.
