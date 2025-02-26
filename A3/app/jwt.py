import base64
import hmac
import hashlib
import json
import time

def generate_jwt(user_id, secret_key):
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": user_id, "exp": int(time.time()) + 3600}
    
    header_b64 = _base64_encode(json.dumps(header))
    payload_b64 = _base64_encode(json.dumps(payload))
    
    signature = hmac.new(
        secret_key.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = _base64_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def _base64_encode(data):
    if isinstance(data, bytes):
        return base64.urlsafe_b64encode(data).decode().rstrip("=")
    else:
        return base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")

def validate_jwt(token, secret_key):
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signature = base64.urlsafe_b64decode(signature_b64 + "===")
        
        expected_signature = hmac.new(
            secret_key.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256
        ).digest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
        
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "==="))
        if payload["exp"] < time.time():
            return None
        
        return payload["sub"]
    except Exception:
        return None