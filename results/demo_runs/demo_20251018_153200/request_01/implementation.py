# main.py
# Production-ready FastAPI user authentication system with bcrypt hashing and JWT token management.
# - Access/Refresh token flow with rotation
# - Secure HttpOnly cookie for refresh token
# - Email verification and password reset via signed, random one-time tokens (stored hashed)
# - SQLAlchemy ORM models and Pydantic schema validation
# - Comprehensive error handling and input validation
#
# NOTE: For demonstration, "email sending" is simulated via logging/print.
# In production, integrate with an email service (SES, SendGrid, Mailgun, etc.).
#
# Dependencies (install via pip):
# fastapi, uvicorn, sqlalchemy, pydantic-settings, python-jose, passlib[bcrypt], email-validator

import os
import sys
import uuid
import secrets
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from fastapi import (
    FastAPI,
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    Response,
    Header,
    Cookie,
)
from fastapi.exceptions import RequestValidationError
from fastapi