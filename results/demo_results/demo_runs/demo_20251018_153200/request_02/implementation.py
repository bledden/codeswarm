# Production-Ready Authentication API with FastAPI, JWT (access + refresh), bcrypt hashing,
# and robust refresh-token storage with rotation and revocation.
#
# Features:
# - /api/v1/auth/register: Register user (creates email verification token)
# - /api/v1/auth/login: Login with email + password (returns access + refresh tokens)
# - /api/v1/auth/refresh: Rotate refresh token, return new pair
# - /api/v1/auth/logout: Revoke a single refresh token
# - /api/v1/auth/logout-all: Revoke all refresh tokens for current user
# - /api/v1/auth/verify-email: Verify email with token
# - /api/v1/auth/forgot-password: Request password reset (token created)
# - /api/v1/auth/reset-password: Reset password with token (revokes all refresh tokens)
# - /api/v1/users/me: Get current user's profile (access token required)
#
# Security:
# - Password hashing with bcrypt via passlib CryptContext
# - JWT access tokens (short-lived) and refresh tokens (long-lived) with jti
# - Refresh tokens stored server-side as SHA-256 hashes with revocation and rotation
# - Token reuse detection: If a revoked refresh token is used, revoke all tokens for that user
# - Email verification / password reset tokens stored hashed with expiry and one-time consumption
#
# Notes:
# - For demonstration, this uses SQLite. For production, use Postgres/MySQL and migrations.
# - Email sending is stubbed (logs). Integrate with an email provider as needed.
# - Cookies are set for refresh_token (HttpOnly). You may opt to manage tokens solely via JSON.
# - Uses async SQLAlchemy 2.0 style with AsyncSession.


import os
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, AsyncGenerator

from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field,