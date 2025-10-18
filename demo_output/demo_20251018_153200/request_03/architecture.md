# Production-Ready Authentication System Architecture

## Executive Summary

This document outlines a comprehensive, production-ready authentication system with JWT-based authentication, rate limiting, and account lockout protection. The architecture is designed for high security, scalability, and maintainability.

## 1. API Endpoint Structure

### 1.1 Authentication Endpoints

```
POST   /api/v1/auth/register          - User registration
POST   /api/v1/auth/login             - User login
POST   /api/v1/auth/refresh           - Refresh access token
POST   /api/v1/auth/logout            - User logout
POST   /api/v1/auth/logout-all        - Logout from all devices
POST   /api/v1/auth/verify-email      - Email verification
POST   /api/v1/auth/resend-verification - Resend verification email
POST   /api/v1/auth/forgot-password   - Request password reset
POST   /api/v1/auth/reset-password    - Reset password with token
POST   /api/v1/auth/change-password   - Change password (authenticated)
GET    /api/v1/auth/me                - Get current user info
POST   /api/v1/auth/unlock-account    - Request account unlock
```

### 1.2 Rate Limiting Configuration

```yaml
Rate Limits:
  /auth/register:        5 requests / 15 minutes / IP
  /auth/login:           5 requests / 15 minutes / IP
  /auth/refresh:         10 requests / 15 minutes / user
  /auth/forgot-password: 3 requests / 1 hour / email
  /auth/verify-email:    5 requests / 1 hour / user
  /auth/resend-verification: 3 requests / 1 hour / user
  
Global API Rate Limit:   100 requests / 15 minutes / IP
```

### 1.3 Request/Response Schemas

#### Registration Request
```json
{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd!",
  "password_confirm": "SecureP@ssw0rd!",
  "first_name": "John",
  "last_name": "Doe",
  "terms_accepted": true
}
```

#### Login Request
```json
{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd!",
  "device_info": {
    "device_name": "Chrome on Windows",
    "device_id": "unique-device-fingerprint",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  }
}
```

#### Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "email_verified": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### Refresh Token Request
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### Error Response
```json
{
  "error": {
    "code": "ACCOUNT_LOCKED",
    "message": "Account locked due to multiple failed login attempts",
    "details": {
      "locked_until": "2024-01-01T01:00:00Z",
      "reason": "exceeded_login_attempts"
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123456"
  }
}
```

## 2. Database Schema

### 2.1 PostgreSQL Schema

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    
    -- Account status
    is_active BOOLEAN DEFAULT TRUE,
    is_locked BOOLEAN DEFAULT FALSE,
    locked_until TIMESTAMP WITH TIME ZONE,
    lock_reason VARCHAR(50),
    
    -- Failed login tracking
    failed_login_attempts INTEGER DEFAULT 0,
    last_failed_login TIMESTAMP WITH TIME ZONE,
    last_successful_login TIMESTAMP WITH TIME ZONE,
    
    -- Password management
    password_changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    password_reset_required BOOLEAN DEFAULT FALSE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_locked ON users(is_locked, locked_until) WHERE is_locked = TRUE;
CREATE INDEX idx_users_active ON users(is_active) WHERE deleted_at IS NULL;

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    
    -- Device information
    device_id VARCHAR(255),
    device_name VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    
    -- Token lifecycle
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_reason VARCHAR(100),
    
    -- Token family for rotation
    token_family UUID NOT NULL,
    parent_token_id UUID REFERENCES refresh_tokens(id),
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash) WHERE revoked = FALSE;
CREATE INDEX idx_refresh_tokens_family ON refresh_tokens(token_family);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at) WHERE revoked = FALSE;

-- Email verification tokens
CREATE TABLE email_verification_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_email_verification_user ON email_verification_tokens(user_id);
CREATE INDEX idx_email_verification_token ON email_verification_tokens(token_hash) 
    WHERE used = FALSE AND expires_at > CURRENT_TIMESTAMP;

-- Password reset tokens
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(