from datetime import datetime, timedelta
import os
import jwt

SECRET_KEY = os.getenv('SECRET_KEY', 'devkey')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*30

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None
