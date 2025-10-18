# Production-Ready Authentication API System Architecture

## Executive Summary

This document outlines a comprehensive authentication system using JWT access tokens and refresh tokens, built on FastAPI with bcrypt password hashing. The architecture prioritizes security, scalability, and maintainability.

## 1. API Endpoint Structure

### 1.1 Authentication Endpoints

```
POST   /api/v1/auth/register          - User registration
POST   /api/v1/auth/login             - User login (returns access + refresh tokens)
POST   /api/v1/auth/refresh           - Refresh access token using refresh token
POST   /api/v1/auth/logout            - Invalidate refresh token
POST   /api/v1/auth/logout-all        - Invalidate all user's refresh tokens
POST   /api/v1/auth/verify-email      - Email verification
POST   /api/v1/auth/forgot-password   - Request password reset
POST   /api/v1/auth/reset-password    - Reset password with token
```

### 1.2 User Management Endpoints

```
GET    /api/v1/users/me               - Get current user profile
PUT    /api/v1/users/me               - Update current user profile
PATCH  /api/v1/users/me/password      - Change password
DELETE /api/v1/users/me               - Delete account
GET    /api/v1/users/me/sessions      - List active sessions
```

### 1.3 Admin Endpoints (Optional)

```
GET    /api/v1/admin/users            - List all users (paginated)
GET    /api/v1/admin/users/{id}       - Get user by ID
PATCH  /api/v1/admin/users/{id}/status - Enable/disable user
DELETE /api/v1/admin/users/{id}       - Delete user
```

### 1.4 Health & Monitoring

```
GET    /health                        - Health check
GET    /metrics                       - Prometheus metrics (if enabled)
```

## 2. Database Schema

### 2.1 PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT username_format CHECK (username ~* '^[a-zA-Z0-9_-]{3,50}$')
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

-- Email verification tokens
CREATE TABLE email_verification_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

-- Password reset tokens
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP WITH TIME ZONE,
    ip_address INET,
    
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

-- Audit log for security events
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_event_type CHECK (event_type IN (
        'login_success', 'login_failed', 'logout', 'password_changed',
        'password_reset_requested', 'password_reset_completed',
        'email_verified', 'account_locked', 'account_unlocked',
        'token_refreshed', 'account_created', 'account_deleted'
    ))
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX idx_email_verification_user_id ON email_verification_tokens(user_id);
CREATE INDEX idx_password_reset_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 2.2 Redis Schema (for token blacklisting and rate limiting)

```
# Blacklisted access tokens (stored until expiry)
Key: blacklist:access:{jti}
Value: user_id
TTL: token expiry time

# Rate limiting
Key: ratelimit:login:{ip_address}
Value: attempt_count
TTL: 900 (15 minutes)

Key: ratelimit:api:{user_id}
Value: request_count
TTL: 60 (1 minute)

# Password reset rate limiting
Key: ratelimit:password_reset:{email}
Value: attempt_count
TTL: 3600 (1 hour)

# Session data (optional)
Key: session:{user_id}:{session_id}
Value: JSON session data
TTL: refresh token expiry
```

## 3. Authentication Flow

### 3.1 Registration Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant DB
    participant Email Service
    
    Client->>API: POST /auth/register
    API->>API: Validate