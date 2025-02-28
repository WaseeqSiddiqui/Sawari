from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ALGORITHM = settings.algorithm
TOKEN_EXPIRY_MINUTES = settings.access_token_minutes
SECRET_KEY = settings.secret_key


def create_access_token(data: dict):
    to_encode = data.copy()
    expiry_minutes = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    to_encode.update({"exp": expiry_minutes})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("user_id")
        role: str = payload.get("role")
        
        if not id or not role:
            raise credentials_exception
        
        return {"user_id": id, "role": role}

    except JWTError as e:
        print(f"JWTError: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return verify_access_token(token, credentials_exception)


def admin_access(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can perform this action")
    return user
