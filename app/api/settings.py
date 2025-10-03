from fastapi import APIRouter, Depends

from app.models.schemas import UserSettings
from app.auth import verify_token

router = APIRouter()


@router.get("/", response_model=UserSettings)
async def get_settings(token: dict = Depends(verify_token)):
    """Get user settings"""
    # TODO: Fetch from BigQuery users table
    return UserSettings(
        currency="KES",
        language="en",
        refresh_frequency="hourly"
    )


@router.put("/", response_model=UserSettings)
async def update_settings(
    settings: UserSettings,
    token: dict = Depends(verify_token)
):
    """Update user settings"""
    # TODO: Update in BigQuery users table
    return settings