
import time
from typing import Dict
import jwt
import os

# Use environment variables with robust fallback defaults
# Try multiple sources: OS environment, then hardcoded defaults
try:
    from decouple import config
    JWT_SECRET = config("secret", default="013aafb560ba561a351e913d3bca0829a290b552")
    JWT_ALGORITHM = config("algorithm", default="HS256")
except Exception:
    # Fallback if decouple fails
    JWT_SECRET = os.environ.get("secret", os.environ.get("JWT_SECRET", "013aafb560ba561a351e913d3bca0829a290b552"))
    JWT_ALGORITHM = os.environ.get("algorithm", os.environ.get("JWT_ALGORITHM", "HS256"))

print(f"JWT Configuration Loaded - Algorithm: {JWT_ALGORITHM}, Secret Length: {len(JWT_SECRET)}")

def token_response(token: str):
    return {
        "access_token": token
    }

def signJWT(client_id: str) -> Dict[str, str]:
    payload = {
        "client_id": client_id,
        "expires": time.time() + 10000
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception as e:
        print(f"JWT Decode Error: {str(e)}")
        return {}    
