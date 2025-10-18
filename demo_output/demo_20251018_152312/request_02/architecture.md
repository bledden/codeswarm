# Production-Ready Authentication API Architecture

## Executive Summary

This document outlines a comprehensive authentication system using JWT access tokens and refresh tokens, built on FastAPI with enterprise-grade security patterns.

## 1. API Endpoint Structure

### 1.1 Authentication Endpoints

```yaml
Base URL: /api/v1/auth

Endpoints:
  POST /register
    Description: Create new user account
    Request Body:
      {
        "email": "string (email format)",
        "password": "string (min 8 chars)",
        "full_name": "string (optional)",
        "username": "string (unique, optional)"
      }
    Response: 201 Created
      {
        "user_id": "uuid",
        "email": "string",
        "full_name": "string",
        "created_at": "datetime"
      }
    Errors: 400 (validation), 409 (conflict)

  POST /login
    Description: Authenticate user and issue tokens
    Request Body:
      {
        "email": "string",
        "password": "string"
      }
    Response: 200 OK
      {
        "access_token": "string (JWT)",
        "refresh_token": "string (JWT)",
        "token_type": "bearer",
        "expires_in": 900,
        "user": {
          "user_id": "uuid",
          "email": "string",
          "full_name": "string"
        }
      }
    Errors: 401 (invalid credentials), 429 (rate limit)

  POST /refresh
    Description: Issue new access token using refresh token
    Request Body:
      {
        "refresh_token": "string"
      }
    Response: 200 OK
      {
        "access_token": "string (JWT)",
        "token_type": "bearer",
        "expires_in": 900
      }
    Errors: 401 (invalid/expired token)

  POST /logout
    Description: Invalidate refresh token
    Headers:
      Authorization: Bearer {access_token}
    Request Body:
      {
        "refresh_token": "string (optional)"
      }
    Response: 204 No Content
    Errors: 401 (unauthorized)

  POST /logout-all
    Description: Invalidate all user sessions
    Headers:
      Authorization: Bearer {access_token}
    Response: 204 No Content
    Errors: 401 (unauthorized)

  POST /forgot-password
    Description: Request password reset
    Request Body:
      {
        "email": "string"
      }
    Response: 202 Accepted
    Note: Always returns 202 to prevent email enumeration

  POST /reset-password
    Description: Reset password with token
    Request Body:
      {
        "token": "string",
        "new_password": "string"
      }
    Response: 200 OK
    Errors: 400 (invalid token), 410 (expired token)

  POST /verify-email
    Description: Verify email address
    Request Body:
      {
        "token": "string"
      }
    Response: 200 OK
    Errors: 400 (invalid token)

  POST /resend-verification
    Description: Resend email verification
    Request Body:
      {
        "email": "string"
      }
    Response: 202 Accepted
```

### 1.2 User Management Endpoints

```yaml
Base URL: /api/v1/users

Endpoints:
  GET /me
    Description: Get current user profile
    Headers:
      Authorization: Bearer {access_token}
    Response: 200 OK
      {
        "user_id": "uuid",
        "email": "string",
        "full_name": "string",
        "username": "string",
        "email_verified": "boolean",
        "created_at": "datetime",
        "updated_at": "datetime"
      }

  PATCH /me
    Description: Update current user profile
    Headers:
      Authorization: Bearer {access_token}
    Request Body:
      {
        "full_name": "string (optional)",
        "username": "string (optional)"
      }
    Response: 200 OK

  POST /me/change-password
    Description: Change user password
    Headers:
      Authorization: Bearer {access_token}
    Request Body:
      {
        "current_password": "string",
        "new_password": "string"
      }
    Response: 200 OK
    Errors: 400 (invalid current password)

  GET /me/sessions
    Description: List active sessions
    Headers:
      Authorization: Bearer {access_token}
    Response: 200 OK
      {
        "sessions": [
          {
            "session_id": "uuid",
            "device_info": "string",
            "ip_address": "string",
            "created_at": "datetime",
            "last_used": "datetime",
            "is_current": "boolean"
          }
        ]
      }

  DELETE /me/sessions/{session_id}
    Description: Revoke specific session
    Headers:
      Authorization: Bearer {access_token}
    Response: 204 No Content
```

## 2. Database Schema

### 2.1 PostgreSQL Schema

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT username_format CHECK (username ~* '^[a-zA-Z0-9_-]{3,50}$')
);

-- Indexes for users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    device_info VARCHAR(500),
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

-- Indexes for refresh_tokens
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_active ON refresh_tokens(user_id, is_revoked) 
    WHERE is_revoked = FALSE;

-- Password reset tokens table
CREATE TABLE password_reset_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_