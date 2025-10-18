# FastAPI User Authentication System Architecture

## Executive Summary

This document outlines a production-ready authentication system built with FastAPI, implementing secure password hashing with bcrypt and JWT-based authentication. The architecture follows industry best practices for security, scalability, and maintainability.

---

## 1. API Endpoint Structure

### 1.1 Authentication Endpoints

```
POST   /api/v1/auth/register          - User registration
POST   /api/v1/auth/login             - User login (returns JWT tokens)
POST   /api/v1/auth/refresh           - Refresh access token
POST   /api/v1/auth/logout            - Invalidate refresh token
POST   /api/v1/auth/password-reset-request  - Request password reset
POST   /api/v1/auth/password-reset    - Reset password with token
GET    /api/v1/auth/verify-email      - Verify email address
POST   /api/v1/auth/resend-verification - Resend verification email
```

### 1.2 User Management Endpoints

```
GET    /api/v1/users/me               - Get current user profile
PUT    /api/v1/users/me               - Update current user profile
PATCH  /api/v1/users/me/password      - Change password
DELETE /api/v1/users/me               - Delete account
```

### 1.3 Endpoint Specifications

#### 1.3.1 User Registration

```python
# Request
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd123",
  "full_name": "John Doe",
  "username": "johndoe"  # optional
}

# Response (201 Created)
{
  "id": "uuid-string",
  "email": "user@example.com",
  "full_name": "John Doe",
  "username": "johndoe",
  "is_active": false,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z",
  "message": "Registration successful. Please verify your email."
}

# Error Response (400 Bad Request)
{
  "detail": "Email already registered"
}
```

#### 1.3.2 User Login

```python
# Request
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd123"
}

# Response (200 OK)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_verified": true
  }
}

# Error Response (401 Unauthorized)
{
  "detail": "Incorrect email or password"
}
```

#### 1.3.3 Token Refresh

```python
# Request
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Response (200 OK)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## 2. Database Schema

### 2.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────┐
│                         users                            │
├─────────────────────────────────────────────────────────┤
│ id                    UUID PRIMARY KEY                   │
│ email                 VARCHAR(255) UNIQUE NOT NULL       │
│ username              VARCHAR(50) UNIQUE                 │
│ hashed_password       VARCHAR(255) NOT NULL              │
│ full_name             VARCHAR(255)                       │
│ is_active             BOOLEAN DEFAULT TRUE               │
│ is_verified           BOOLEAN DEFAULT FALSE              │
│ is_superuser          BOOLEAN DEFAULT FALSE              │
│ created_at            TIMESTAMP DEFAULT NOW()            │
│ updated_at            TIMESTAMP DEFAULT NOW()            │
│ last_login            TIMESTAMP                          │
│ failed_login_attempts INTEGER DEFAULT 0                  │
│ locked_until          TIMESTAMP                          │
└─────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   refresh_tokens                         │
├─────────────────────────────────────────────────────────┤
│ id                    UUID PRIMARY KEY                   │
│ user_id               UUID FOREIGN KEY → users(id)       │
│ token_hash            VARCHAR(255) UNIQUE NOT NULL       │
│ expires_at            TIMESTAMP NOT NULL                 │
│ created_at            TIMESTAMP DEFAULT NOW()            │
│ revoked               BOOLEAN DEFAULT FALSE              │
│ revoked_at            TIMESTAMP                          │
│ device_info           JSONB                              │
│ ip_address            INET                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 password_reset_tokens                    │
├─────────────────────────────────────────────────────────┤
│ id                    UUID PRIMARY KEY                   │
│ user_id               UUID FOREIGN KEY → users(id)       │
│ token_hash            VARCHAR(255) UNIQUE NOT NULL       │
│ expires_at            TIMESTAMP NOT NULL                 │
│ created_at            TIMESTAMP DEFAULT NOW()            │
│ used                  BOOLEAN DEFAULT FALSE              │
│ used_at               TIMESTAMP                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                email_verification_tokens                 │
├─────────────────────────────────────────────────────────┤
│ id                    UUID PRIMARY KEY                   │
│ user_id               UUID FOREIGN KEY → users(id)       │
│ token_hash            VARCHAR(255) UNIQUE NOT NULL       │
│ expires_at            TIMESTAMP NOT NULL                 │
│ created_at            TIMESTAMP DEFAULT NOW()            │
│ verified              BOOLEAN DEFAULT FALSE              │
│ verified_at           TIMESTAMP                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                     audit_logs                           │
├─────────────────────────────────────────────────────────┤
│ id                    UUID PRIMARY KEY                   │
│ user_id               UUID FOREIGN KEY → users(id)       │
│ action                VARCHAR(100) NOT NULL              │
│ ip_address            INET                               │
│ user_agent            TEXT                               │
│ metadata              JSONB                              │
│ created_at            TIMESTAMP DEFAULT NOW()            │
└─────────────────────────────────────────────────────────┘
```

### 2.2 SQLAlchemy Models

```python
# models/user.py
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Boolean, Column