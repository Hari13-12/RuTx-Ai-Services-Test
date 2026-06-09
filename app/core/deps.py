from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core import token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token_str: str = Depends(oauth2_scheme)):
    try:
        payload = await token.decode_token(token_str)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )