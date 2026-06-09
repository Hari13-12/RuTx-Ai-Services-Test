from datetime import datetime, timedelta, timezone
from typing import Dict
import os
import base64, json, hmac, hashlib

# Hardcode algorithm
JWT_ALGORITHM = "HS256"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign_hs256(message: bytes, secret: str) -> str:
    sig = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).digest()
    return _b64url_encode(sig)


async def create_access_token(username: str, expires_minutes: int = None) -> str:
    """
    Create JWT Access Token

    Args:
        username (str): The username to encode
        expires_minutes (int, optional): Expiry in minutes. Defaults to os.getenv(ACCESS_TOKEN_EXPIRE_MINUTES).

    Returns:
        str: JWT access token
    """
    if not expires_minutes:
        expires_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {
        "sub": username,
        "exp": int(expire.timestamp())
    }

    # JWT header
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(',', ':')).encode())
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(',', ':')).encode())

    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature_b64 = _sign_hs256(signing_input, os.getenv("SECRET_KEY"))
   

    return f"{header_b64}.{payload_b64}.{signature_b64}"


async def decode_token(token: str) -> Dict:
    """
    Decode and verify JWT Access Token

    Args:
        token (str): JWT string

    Returns:
        dict: Decoded payload
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = _sign_hs256(signing_input, os.getenv("SECRET_KEY"))
        

        if not hmac.compare_digest(signature_b64, expected_sig):
            raise ValueError("Invalid signature")

        payload = json.loads(_b64url_decode(payload_b64))

        if "exp" in payload and datetime.now(timezone.utc).timestamp() >= float(payload["exp"]):
            raise ValueError("Token expired")

        return payload
    except Exception as e:
        raise ValueError(f"Invalid token: {str(e)}")