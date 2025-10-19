"""Data quality API endpoints"""

from fastapi import APIRouter, Depends

from app.auth import verify_token
from app.services.data_quality import data_quality_checker

router = APIRouter()


@router.get("/check")
async def check_data_quality(token: dict = Depends(verify_token)):
    """Run data quality checks"""
    user_id = token.get("sub")
    return data_quality_checker.run_checks(user_id)