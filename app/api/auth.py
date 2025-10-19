"""Authentication endpoints for frontend"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from datetime import timedelta, datetime
import logging
import hashlib
import secrets
import json

from app.auth import create_access_token, verify_token
from app.config import settings
from app.utils.bigquery_client import bq_client

router = APIRouter()
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    business_name: str = Field(..., min_length=2)
    full_name: str = Field(..., min_length=2)
    currency: str = "KES"
    language: str = "en"


class UserResponse(BaseModel):
    user_id: str
    email: str
    business_name: str
    full_name: str
    currency: str
    language: str


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{pwd_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, pwd_hash = stored_hash.split(':')
        test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return test_hash == pwd_hash
    except:
        return False


def get_user_by_email(email: str):
    """Get user from BigQuery by email"""
    try:
        query = f"""
        SELECT 
            id,
            email,
            password_hash,
            business_name,
            full_name,
            currency,
            language,
            created_at
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.users`
        WHERE email = @email
        LIMIT 1
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter('email', 'STRING', email)
            ]
        )
        
        results = list(bq_client.client.query(query, job_config=job_config).result())
        
        if results:
            return dict(results[0])
        return None
        
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None


def create_user(email: str, password: str, business_name: str, 
                full_name: str, currency: str = "KES", language: str = "en"):
    """Create new user in BigQuery"""
    try:
        user_id = f"user-{secrets.token_hex(8)}"
        password_hash = hash_password(password)
        
        # Format timestamp as string (BigQuery batch load requirement)
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create user record with all fields as strings/primitives
        user_record = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "business_name": business_name,
            "full_name": full_name,
            "currency": currency,
            "language": language,
            "refresh_frequency": "hourly",
            "settings": "",  # Empty string instead of dict
            "created_at": now,
            "updated_at": now
        }
        
        logger.info(f"Inserting user record: {user_record}")
        
        # Insert into BigQuery
        bq_client.insert_rows("users", [user_record])
        
        logger.info(f"User created successfully: {email}")
        
        return {
            "id": user_id,
            "email": email,
            "business_name": business_name,
            "full_name": full_name,
            "currency": currency,
            "language": language
        }
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise


@router.post("/register", response_model=LoginResponse)
async def register(data: RegisterRequest):
    """
    Register new user
    
    - Creates user account in BigQuery
    - Hashes password securely
    - Returns JWT token
    """
    try:
        # Check if user already exists
        existing_user = get_user_by_email(data.email)
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = create_user(
            email=data.email,
            password=data.password,
            business_name=data.business_name,
            full_name=data.full_name,
            currency=data.currency,
            language=data.language
        )
        
        # Generate JWT token
        token = create_access_token(
            data={
                "sub": user["id"],
                "email": user["email"],
                "business_name": user["business_name"]
            },
            expires_delta=timedelta(hours=24)
        )
        
        logger.info(f"User registered successfully: {user['email']}")
        
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user={
                "id": user["id"],
                "email": user["email"],
                "business_name": user["business_name"],
                "full_name": user["full_name"],
                "currency": user["currency"],
                "language": user["language"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Login user
    
    - Validates email and password
    - Returns JWT token on success
    """
    try:
        # Get user from database
        user = get_user_by_email(credentials.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate JWT token
        token = create_access_token(
            data={
                "sub": user["id"],
                "email": user["email"],
                "business_name": user["business_name"]
            },
            expires_delta=timedelta(hours=24)
        )
        
        logger.info(f"User logged in: {user['email']}")
        
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user={
                "id": user["id"],
                "email": user["email"],
                "business_name": user["business_name"],
                "full_name": user["full_name"],
                "currency": user.get("currency", "KES"),
                "language": user.get("language", "en")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: dict = Depends(verify_token)):
    """
    Get current user information
    
    Requires valid JWT token
    """
    try:
        user_id = token.get("sub")
        email = token.get("email")
        
        # Get full user details
        user = get_user_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            user_id=user["id"],
            email=user["email"],
            business_name=user["business_name"],
            full_name=user["full_name"],
            currency=user.get("currency", "KES"),
            language=user.get("language", "en")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.post("/refresh", response_model=dict)
async def refresh_token(token: dict = Depends(verify_token)):
    """
    Refresh JWT token
    
    Returns new token with extended expiry
    """
    try:
        new_token = create_access_token(
            data={
                "sub": token.get("sub"),
                "email": token.get("email"),
                "business_name": token.get("business_name")
            },
            expires_delta=timedelta(hours=24)
        )
        
        return {
            "access_token": new_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@router.post("/logout")
async def logout(token: dict = Depends(verify_token)):
    """
    Logout user
    
    Note: JWT tokens are stateless, so logout is handled client-side
    This endpoint exists for logging purposes
    """
    user_id = token.get("sub")
    logger.info(f"User logged out: {user_id}")
    
    return {
        "status": "success",
        "message": "Logged out successfully"
    }