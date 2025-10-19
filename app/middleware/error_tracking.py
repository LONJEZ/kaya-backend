"""Middleware to track errors"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.error_tracker import error_tracker
import logging

logger = logging.getLogger(__name__)


class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    """Track errors automatically"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            
            # Track 4xx and 5xx responses
            if response.status_code >= 400:
                error_tracker.track_error(
                    error_type=f"HTTP_{response.status_code}",
                    error_message=f"HTTP error {response.status_code}",
                    endpoint=request.url.path,
                    user_id=getattr(request.state, "user_id", None)
                )
            
            return response
            
        except Exception as e:
            error_tracker.track_error(
                error_type=type(e).__name__,
                error_message=str(e),
                endpoint=request.url.path,
                user_id=getattr(request.state, "user_id", None),
                context={"method": request.method}
            )
            raise