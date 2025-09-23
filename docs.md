# FastAPI Microservice Development with PostgreSQL and Kubernetes

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Application Components](#application-components)
5. [Database Layer](#database-layer)
6. [API Layer](#api-layer)
7. [Kubernetes Deployment](#kubernetes-deployment)
8. [Docker Containerization](#docker-containerization)
9. [Development Workflow](#development-workflow)
10. [Learning Resources](#learning-resources)

## Overview

This documentation explains a FastAPI microservice architecture designed for user management, including authentication and profile management. The application demonstrates modern Python web development practices using FastAPI, PostgreSQL, Docker, and Kubernetes deployment.

### Key Technologies
- **FastAPI**: Modern, fast Python web framework for building APIs
- **PostgreSQL**: Robust relational database for data persistence
- **SQLAlchemy**: Python SQL toolkit and Object Relational Mapping (ORM)
- **Pydantic**: Data validation using Python type annotations
- **Docker**: Containerization platform
- **Kubernetes**: Container orchestration platform
- **Skaffold**: Tool for continuous development for Kubernetes applications

### Learning Objectives
This codebase is designed to teach:
- Modern Python web API development
- Database integration and ORM usage
- Containerization best practices
- Kubernetes deployment patterns
- Microservice architecture principles

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client/UI     │    │   Load Balancer │    │   Kubernetes    │
│                 │────│                 │────│    Cluster      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                               ┌─────────────────┐
                                               │  FastAPI Pod    │
                                               │                 │
                                               │  ┌───────────┐  │
                                               │  │   API     │  │
                                               │  │  Routes   │  │
                                               │  └───────────┘  │
                                               │  ┌───────────┐  │
                                               │  │ Business  │  │
                                               │  │   Logic   │  │
                                               │  └───────────┘  │
                                               │  ┌───────────┐  │
                                               │  │   Data    │  │
                                               │  │   Layer   │  │
                                               │  └───────────┘  │
                                               └─────────────────┘
                                                       │
                                               ┌─────────────────┐
                                               │ PostgreSQL Pod  │
                                               │                 │
                                               │ ┌─────────────┐ │
                                               │ │   Database  │ │
                                               │ │   Storage   │ │
                                               │ └─────────────┘ │
                                               └─────────────────┘
```

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── db.py               # Database configuration and connection
├── models.py           # SQLAlchemy database models
├── schemas.py          # Pydantic schemas for request/response validation
└── routers/
    └── users.py        # User management API endpoints

k8s/
├── app-db.secret.yaml          # Database credentials (Kubernetes Secret)
├── postgres.service.yaml       # PostgreSQL service definition
├── postgres.statefulset.yaml   # PostgreSQL StatefulSet deployment
├── hello-api.deployment.yaml   # FastAPI application deployment
└── hello-api.service.yaml      # FastAPI service definition

Dockerfile              # Container image definition
requirements.txt        # Python dependencies
skaffold.yaml           # Skaffold configuration for development
```

## Application Components

### 1. Main Application (`app/main.py`)

The entry point of the FastAPI application that configures the web server and includes routers.

```python
from fastapi import FastAPI
from app.routers import users
from app.db import create_tables

app = FastAPI(
    title="User Management API",
    description="A FastAPI microservice for user management",
    version="1.0.0"
)

# Include routers
app.include_router(users.router, prefix="/api/v1", tags=["users"])

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    await create_tables()

@app.get("/")
def read_root():
    """Root endpoint for basic API information"""
    return {
        "message": "User Management API",
        "version": app.version,
        "docs_url": "/docs"
    }

@app.get("/healthz")
def health_check():
    """Health check endpoint for Kubernetes liveness probe"""
    return {"status": "healthy"}

@app.get("/readyz")
def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probe"""
    return {"status": "ready"}
```

**Key Concepts:**
- **FastAPI instance**: Creates the main application object
- **Router inclusion**: Modular approach to organize endpoints
- **Startup events**: Initialization logic that runs when the app starts
- **Health endpoints**: Essential for Kubernetes health monitoring

### 2. Database Configuration (`app/db.py`)

Manages database connections using async SQLAlchemy for optimal performance.

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
import os

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://user:password@postgres:5432/userdb"
)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Create database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

**Key Concepts:**
- **Async SQLAlchemy**: Non-blocking database operations for better performance
- **Connection pooling**: Efficiently manages database connections
- **Dependency injection**: `get_db()` provides database sessions to endpoints
- **Environment variables**: Configuration through environment variables

### 3. Database Models (`app/models.py`)

Defines the database schema using SQLAlchemy ORM.

```python
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db import Base
from datetime import datetime

class User(Base):
    """User model representing users table"""
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # User information
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
```

**Key Concepts:**
- **ORM Mapping**: Python classes mapped to database tables
- **Type annotations**: Modern SQLAlchemy 2.0 syntax with type hints
- **Constraints**: Unique constraints and indexes for data integrity
- **Timestamps**: Automatic creation and update time tracking

### 4. Pydantic Schemas (`app/schemas.py`)

Defines data validation and serialization schemas.

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8)
    
    class Config:
        # Example for documentation
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "password": "secretpassword"
            }
        }

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """Schema for user response (excludes sensitive data)"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Enable ORM mode

class UserList(BaseModel):
    """Schema for paginated user list"""
    users: list[UserResponse]
    total: int
    page: int
    size: int
```

**Key Concepts:**
- **Data validation**: Automatic validation of request/response data
- **Type safety**: Python type hints for better code quality
- **Serialization**: Convert between Python objects and JSON
- **Documentation**: Automatic API documentation generation

## API Layer

### 5. User Routes (`app/routers/users.py`)

Implements the RESTful API endpoints for user management.

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.db import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserUpdate, UserList

router = APIRouter()

@router.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user"""
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, 
            detail="User with this email already exists"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        # Note: In production, hash the password!
        # password_hash=hash_password(user_data.password)
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

@router.get("/users/", response_model=UserList)
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List users with pagination"""
    offset = (page - 1) * size
    
    # Get total count
    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar()
    
    # Get paginated users
    result = await db.execute(
        select(User)
        .offset(offset)
        .limit(size)
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    
    return UserList(
        users=users,
        total=total,
        page=page,
        size=size
    )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user information"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update only provided fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a user"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    
    return {"message": "User deleted successfully"}
```

**Key Concepts:**
- **RESTful design**: Standard HTTP methods for CRUD operations
- **Dependency injection**: Database session and authentication dependencies
- **Error handling**: Proper HTTP status codes and error messages
- **Async operations**: Non-blocking database operations
- **Pagination**: Efficient handling of large datasets

## Kubernetes Deployment

### 6. Database Secret (`k8s/app-db.secret.yaml`)

Stores sensitive database configuration securely.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-db-secret
  namespace: default
type: Opaque
data:
  # Base64 encoded values
  database-url: cG9zdGdyZXNxbCthc3luY3BnOi8vdXNlcjpwYXNzd29yZEBwb3N0Z3Jlczo1NDMyL3VzZXJkYg==
  postgres-user: dXNlcg==
  postgres-password: cGFzc3dvcmQ=
  postgres-db: dXNlcmRi
```

**Key Concepts:**
- **Secrets management**: Secure storage of sensitive data
- **Base64 encoding**: Kubernetes secret data format
- **Environment separation**: Different secrets per environment

### 7. PostgreSQL Service (`k8s/postgres.service.yaml`)

Defines network access to the PostgreSQL database.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  labels:
    app: postgres
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
      protocol: TCP
      name: postgres
  selector:
    app: postgres
```

**Key Concepts:**
- **Service discovery**: Internal DNS resolution for database access
- **Port mapping**: Expose database port within the cluster
- **Label selectors**: Connect service to specific pods

### 8. PostgreSQL StatefulSet (`k8s/postgres.statefulset.yaml`)

Manages the PostgreSQL database deployment with persistent storage.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15
          ports:
            - containerPort: 5432
              name: postgres
          env:
            - name: POSTGRES_DB
              valueFrom:
                secretKeyRef:
                  name: app-db-secret
                  key: postgres-db
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: app-db-secret
                  key: postgres-user
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: app-db-secret
                  key: postgres-password
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
  volumeClaimTemplates:
    - metadata:
        name: postgres-storage
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi
```

**Key Concepts:**
- **StatefulSet**: Manages stateful applications with persistent identity
- **Persistent volumes**: Data persistence across pod restarts
- **Resource limits**: CPU and memory constraints for stability
- **Secret references**: Secure environment variable injection

### 9. API Deployment (`k8s/hello-api.deployment.yaml`)

Deploys the FastAPI application with high availability and health checks.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-api
  labels:
    app: hello-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hello-api
  template:
    metadata:
      labels:
        app: hello-api
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
      containers:
        - name: hello-api
          image: hello-api
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
              name: http
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: app-db-secret
                  key: database-url
            - name: APP_ENV
              value: "production"
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
```

**Key Concepts:**
- **Horizontal scaling**: Multiple replicas for high availability
- **Health probes**: Automatic health monitoring and recovery
- **Security context**: Container security best practices
- **Resource management**: CPU and memory allocation

### 10. API Service (`k8s/hello-api.service.yaml`)

Exposes the FastAPI application within the cluster.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: hello-api
  labels:
    app: hello-api
spec:
  type: ClusterIP
  selector:
    app: hello-api
  ports:
    - name: http
      port: 8000
      targetPort: http
      protocol: TCP
```

## Docker Containerization

### 11. Dockerfile

Multi-stage Docker build for optimized container images.

```dockerfile
# Builder stage for dependencies
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    PORT=8000

WORKDIR /app

# Create non-root user for security
RUN useradd -u 10001 -s /usr/sbin/nologin appuser && \
    mkdir -p /app && chown -R appuser:appuser /app

# Copy virtual environment from builder
COPY --from=builder /venv /venv

# Copy application code
COPY app/ /app/

# Switch to non-root user
USER 10001:10001

# Expose application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key Concepts:**
- **Multi-stage builds**: Smaller production images by excluding build tools
- **Non-root user**: Security best practice to avoid privilege escalation
- **Health checks**: Container-level health monitoring
- **Environment optimization**: Python-specific optimizations

## Development Workflow

### 12. Skaffold Configuration (`skaffold.yaml`)

Continuous development workflow for Kubernetes.

```yaml
apiVersion: skaffold/v4beta11
kind: Config
metadata:
  name: user-management-api

# Build configuration
build:
  local:
    push: false
  artifacts:
    - image: hello-api
      context: .
      docker:
        dockerfile: Dockerfile

# Deploy configuration
deploy:
  kubectl: {}

# Kubernetes manifests
manifests:
  rawYaml:
    - k8s/*.yaml

# Development features
portForward:
  - resourceType: service
    resourceName: hello-api
    port: 8000
    localPort: 8000

# File watching for auto-rebuild
build:
  tagPolicy:
    gitCommit: {}
```

**Key Concepts:**
- **Continuous development**: Automatic rebuild and redeploy on code changes
- **Port forwarding**: Local access to cluster services
- **Image tagging**: Consistent image versioning with git commits

### 13. Requirements (`requirements.txt`)

Python dependencies for the application.

```txt
# Web framework
fastapi>=0.115,<1.0
uvicorn[standard]>=0.30,<1.0

# Database
sqlalchemy[asyncio]>=2.0,<3.0
asyncpg>=0.29,<1.0
alembic>=1.13,<2.0

# Data validation
pydantic>=2.0,<3.0
pydantic[email]>=2.0,<3.0

# Authentication (for future implementation)
python-jose[cryptography]>=3.3,<4.0
passlib[bcrypt]>=1.7,<2.0
python-multipart>=0.0.9

# Development and testing
pytest>=8.0,<9.0
pytest-asyncio>=0.24,<1.0
httpx>=0.27,<1.0
```

## Learning Resources

### For Kubernetes Beginners

1. **Core Concepts to Understand:**
   - Pods: Smallest deployable units
   - Services: Network access to pods
   - Deployments: Managing pod replicas
   - ConfigMaps/Secrets: Configuration management
   - Persistent Volumes: Data storage

2. **Recommended Learning Path:**
   ```bash
   # Start with basic concepts
   kubectl get pods
   kubectl get services
   kubectl get deployments
   
   # Examine our application
   kubectl describe deployment hello-api
   kubectl logs -f deployment/hello-api
   
   # Debug issues
   kubectl exec -it <pod-name> -- /bin/bash
   ```

### For Python/FastAPI Development

1. **Key Patterns Demonstrated:**
   - Dependency injection with `Depends()`
   - Async/await for database operations
   - Pydantic models for data validation
   - Router organization for modularity

2. **Development Workflow:**
   ```bash
   # Local development
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   
   # Database migrations (future)
   alembic init alembic
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

### Best Practices Implemented

1. **Security:**
   - Non-root container users
   - Read-only root filesystem
   - Secret management for sensitive data
   - Input validation with Pydantic

2. **Reliability:**
   - Health checks at multiple levels
   - Resource limits and requests
   - Graceful error handling
   - Database connection pooling

3. **Observability:**
   - Structured logging
   - Health endpoints
   - Application metrics (extensible)

### Next Steps for Enhancement

1. **Authentication & Authorization:**
   ```python
   # JWT token implementation
   from jose import JWTError, jwt
   from passlib.context import CryptContext
   
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   ```

2. **Database Migrations:**
   ```bash
   # Add Alembic for schema management
   alembic init migrations
   alembic revision --autogenerate -m "Add user table"
   ```

3. **Testing:**
   ```python
   # Comprehensive test suite
   import pytest
   from httpx import AsyncClient
   from app.main import app
   
   @pytest.mark.asyncio
   async def test_create_user():
       async with AsyncClient(app=app, base_url="http://test") as ac:
           response = await ac.post("/api/v1/users/", json={...})
           assert response.status_code == 201
   ```

4. **Monitoring:**
   - Prometheus metrics integration
   - Distributed tracing with OpenTelemetry
   - Centralized logging with ELK stack

This documentation provides a comprehensive foundation for understanding modern microservice development with Python, FastAPI, and Kubernetes. The architecture demonstrated here follows industry best practices and provides a solid foundation for scaling and extending the application.