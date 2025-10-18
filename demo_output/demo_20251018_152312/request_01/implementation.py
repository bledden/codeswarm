# main.py
# Production-ready FastAPI user authentication with bcrypt password hashing and JWT-based auth.
# Features:
# - Registration with email verification
# - Login with access and refresh JWT tokens
# - Token refresh with rotation and revocation
# - Logout (invalidate refresh token)
# - Password reset (request + confirm)
# - Get current user (/users/me)
# - Robust input validation and error handling
# - SQLAlchemy models and SQLite DB for demo (works with Postgres by changing DATABASE_URL)
# - Well-commented for clarity

import os
import sys
import hmac
import uuid
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Generator, Optional, Tuple

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, BaseSettings, EmailStr, Field, validator
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Index,
    UniqueConstraint,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from jose import jwt, JWTError
from passlib.context import CryptContext


# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

class Settings(BaseSettings):
    # Security
    JWT_SECRET_KEY: str = Field("dev-secret-change-me", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database (use SQLite for demo; set to Postgres in production)
    DATABASE_URL: str = Field("sqlite:///./auth_demo.db", env="DATABASE_URL")

    # App
    PROJECT_NAME: str = "Auth API"
    API_V1_PREFIX: str = "/api/v1"
    # For email links (simulate email sending)
    BASE_BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_BASE_URL: str = "http://localhost:3000"

    # CORS (development defaults)
    CORS_ALLOW_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------

logger = logging.getLogger("auth_api")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ------------------------------------------------------------------------------
# Database setup (SQLAlchemy)
# ------------------------------------------------------------------------------

connect_args =