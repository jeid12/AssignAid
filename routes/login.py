from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.Login import UserLogin
from database import user_collection
from passlib.context import CryptContext
from bson import ObjectId
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# JWT configurations
SECRET_KEY = "your_secret_key"  # Make sure to replace with a secure secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Set token expiration to 1 hour

router = APIRouter()

# Initialize password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer to get the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Helper function to verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Helper function to authenticate user
async def authenticate_user(username: str, password: str):
    user = await user_collection.find_one({"username": username})
    if not user or not verify_password(password, user["password"]):
        return False
    return user

# Create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Login route
@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    
    # Create token with user role
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},  # Include role in token
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")  # Retrieve role from token
        if username is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await user_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

# Protected route example
@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

# Optional: You can add role-based access control in other routes by checking current_user['role']
