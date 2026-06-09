import os
import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.login_request import LoginRequest
from app.core.token import create_access_token
import os



router = APIRouter()


AUTH_USERNAME = os.getenv("AUTH_USERNAME")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")

@router.post("/auth_token")
async def auth_token(request: LoginRequest):
    logger = logging.getLogger(__name__)
    try:
        username = request.username
        password = request.password

        # Validate against env credentials
        if username != AUTH_USERNAME or password != AUTH_PASSWORD:
            logger.warning("Authentication failed", extra={"username": username})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        # Create JWT access token
        access_token = await create_access_token(username=username)
        logger.info("Authentication successful", extra={"username": username})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        # pass through known HTTP errors
        raise
    except Exception as exc:
        logger.exception("Unhandled error in auth_token")
        raise HTTPException(
            status_code=status,
            detail="Authentication service error",
        ) from exc
