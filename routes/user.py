from fastapi import APIRouter, HTTPException, Form
from models.UserRegister import RoleEnum, UserRegistration, UserRegistrationResponse
from database import user_collection
from passlib.context import CryptContext
from bson import ObjectId
from typing import Optional

router = APIRouter()

# Password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper function to hash passwords
def hash_password(password: str):
    return pwd_context.hash(password)

# Helper function to convert MongoDB ObjectId to string
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "FullName": user["FullName"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "gender": user["gender"]
    }

# Register a new user
@router.post("/register", response_model=UserRegistrationResponse)
async def register_user(
    FullName: str = Form(...),
    username: str = Form(..., min_length=6, max_length=12),
    email: str = Form(...),
    password: str = Form(..., min_length=8, max_length=60),  # Updated max_length
    role: RoleEnum = Form(...),
    gender: str = Form(...)
):
    # Check if username or email already exists
    if await user_collection.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    if await user_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = hash_password(password)

    # Create the user object
    user = {
        "FullName": FullName,
        "username": username,
        "email": email,
        "password": hashed_password,  # Store hashed password
        "role": role,
        "gender": gender
    }

    # Insert the user into the database
    new_user = await user_collection.insert_one(user)
    created_user = await user_collection.find_one({"_id": new_user.inserted_id})

    # Return the response using UserRegistrationResponse
    return UserRegistrationResponse(
        id=str(created_user["_id"]),
        FullName=created_user["FullName"],
        username=created_user["username"],
        email=created_user["email"],
        role=created_user["role"],
        gender=created_user["gender"]
    )

# Add the remaining routes here (get_user, get_users, update_user, delete_user)



# Get user by ID
@router.get("/{id}", response_model=UserRegistration)
async def get_user(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_helper(user)

# Get all users
@router.get("/", response_model=Optional[list])
async def get_users():
    users = []
    async for user in user_collection.find():
        users.append(user_helper(user))
    return users

# Update user by ID
@router.put("/{id}", response_model=UserRegistration)
async def update_user(
    id: str,
    FullName: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    role: Optional[RoleEnum] = Form(None),
    gender: Optional[str] = Form(None)
):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    update_data = {}

    if FullName:
        update_data["FullName"] = FullName
    if username:
        # Ensure new username is unique
        if await user_collection.find_one({"username": username}):
            raise HTTPException(status_code=400, detail="Username already exists")
        update_data["username"] = username
    if email:
        # Ensure new email is unique
        if await user_collection.find_one({"email": email}):
            raise HTTPException(status_code=400, detail="Email already registered")
        update_data["email"] = email
    if password:
        hashed_password = hash_password(password)
        update_data["password"] = hashed_password
    if role:
        update_data["role"] = role
    if gender:
        update_data["gender"] = gender

    # Update the user in the database
    update_result = await user_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await user_collection.find_one({"_id": ObjectId(id)})
    return user_helper(updated_user)

# Delete user by ID
@router.delete("/{id}")
async def delete_user(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    delete_result = await user_collection.delete_one({"_id": ObjectId(id)})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}
