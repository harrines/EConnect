
import time
from typing import Dict
import jwt
import os

# Valid JWT algorithms
VALID_ALGORITHMS = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]

# Use environment variables with robust fallback defaults
# Try multiple sources: OS environment, then hardcoded defaults
try:
    from decouple import config
    # Try both old and new environment variable names
    JWT_SECRET = config("JWT_SECRET", default=config("secret", default="013aafb560ba561a351e913d3bca0829a290b552"))
    JWT_ALGORITHM = config("JWT_ALGORITHM", default=config("algorithm", default="HS256"))
except Exception as e:
    # Fallback if decouple fails - check multiple environment variable names
    JWT_SECRET = os.environ.get("JWT_SECRET") or os.environ.get("secret") or "013aafb560ba561a351e913d3bca0829a290b552"
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM") or os.environ.get("algorithm") or "HS256"

# Validate algorithm - if invalid, use default HS256
if JWT_ALGORITHM not in VALID_ALGORITHMS:
    print(f"WARNING: Invalid JWT algorithm '{JWT_ALGORITHM}'. Using default 'HS256'")
    JWT_ALGORITHM = "HS256"

print(f"JWT Configuration Loaded - Algorithm: {JWT_ALGORITHM}, Secret Length: {len(JWT_SECRET)}")

def token_response(token: str):
    return {
        "access_token": token
    }

def signJWT(client_id: str) -> Dict[str, str]:
    try:
        payload = {
            "client_id": client_id,
            "expires": time.time() + 10000
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        return token_response(token)
    except Exception as e:
        print(f"JWT Encode Error: {str(e)}")
        print(f"Algorithm used: {JWT_ALGORITHM}")
        print(f"Secret length: {len(JWT_SECRET)}")
        raise Exception(f"Failed to generate JWT token: {str(e)}")

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception as e:
        print(f"JWT Decode Error: {str(e)}")
        return {}
