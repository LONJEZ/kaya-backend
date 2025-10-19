"""Authentication endpoints for frontend"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import timedelta
import logging

from app.auth import create_access_token, verify_token
from app.config import settings
from app.utils.bigquery_client import bq_client

router = APIRouter()
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    business_name: str
    full_name: str
    currency: str = "KES"
    language: str = "en"


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Login endpoint
    For demo: accepts any email/password
    Production: integrate with proper auth system
    """
    
    # TODO: Add proper password verification
    # For now, create