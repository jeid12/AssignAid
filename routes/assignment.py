from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from models.Assignment import Assignment
from database import assignment_collection, user_collection
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
import shutil
import os
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

router = APIRouter()

# Path to save uploaded files
UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# JWT configurations
SECRET_KEY = "your_secret_key"  # Use your actual secret key
ALGORITHM = "HS256"

# OAuth2PasswordBearer to get the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Helper function to convert MongoDB ObjectId to string
def assignment_helper(assignment) -> dict:
    return {
        "id": str(assignment["_id"]),
        "title": assignment["title"],
        "description": assignment["description"],
        "subject": assignment["subject"],
        "files": assignment["files"],
        "created_by": assignment["created_by"],
        "status": assignment["status"],
        "due_date": assignment["due_date"],
        "created_at": assignment.get("created_at")  # Use get to avoid KeyError
    }

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
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Fetch user from users_collection
    user = await user_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

# Create a new assignment with file upload and form data
@router.post("/", response_model=Assignment)
async def create_assignment(
    title: str = Form(...),
    description: str = Form(...),
    subject: str = Form(...),
    status: Optional[str] = Form("pending"),
    due_date: Optional[datetime] = Form(None),
    current_user: dict = Depends(get_current_user),  # Get current user
    files: Optional[List[UploadFile]] = File(None)
):
    file_paths = []
    
    # Save uploaded files and store their paths
    if files:
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            file_paths.append(file_path)  # Store file path

    # Build Assignment instance using form data and saved file paths
    assignment = Assignment(
        title=title,
        description=description,
        subject=subject,
        files=file_paths,
        created_by=current_user['username'],  # Use current user's username
        status=status,
        due_date=due_date,
        created_at=datetime.utcnow()  # Add created timestamp
    )
    
    # Convert assignment model to dict and insert into database
    assignment_dict = assignment.dict()
    new_assignment = await assignment_collection.insert_one(assignment_dict)
    created_assignment = await assignment_collection.find_one({"_id": new_assignment.inserted_id})

    return assignment_helper(created_assignment)

# Get all assignments
@router.get("/", response_model=List[Assignment])
async def get_assignments():
    assignments = []
    async for assignment in assignment_collection.find():
        assignments.append(assignment_helper(assignment))
    return assignments

# Get a single assignment by ID
@router.get("/{id}", response_model=Assignment)
async def get_assignment(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    assignment = await assignment_collection.find_one({"_id": ObjectId(id)})
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment_helper(assignment)

# Update an assignment by ID (allows updating with files)
@router.put("/{id}", response_model=Assignment)
async def update_assignment(
    id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    due_date: Optional[datetime] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    current_user: dict = Depends(get_current_user)  # Get current user
):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    assignment_data = {}

    if title:
        assignment_data["title"] = title
    if description:
        assignment_data["description"] = description
    if subject:
        assignment_data["subject"] = subject
    if status:
        assignment_data["status"] = status
    if due_date:
        assignment_data["due_date"] = due_date
    
    # Save uploaded files if any
    if files:
        assignment_data["files"] = []
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            assignment_data["files"].append(file_path)

    # Update the assignment in the database
    update_result = await assignment_collection.update_one({"_id": ObjectId(id)}, {"$set": assignment_data})
    
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    updated_assignment = await assignment_collection.find_one({"_id": ObjectId(id)})
    return assignment_helper(updated_assignment)

# Delete an assignment by ID
@router.delete("/{id}")
async def delete_assignment(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    delete_result = await assignment_collection.delete_one({"_id": ObjectId(id)})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    return {"message": "Assignment deleted successfully"}
