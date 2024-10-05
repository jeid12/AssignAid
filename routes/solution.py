from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from models.Solution import Solution
from database import solution_collection
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
import shutil
import os
from routes.login import get_current_user  # Import to access current user

router = APIRouter()

# Path to save uploaded solution files
SOLUTION_UPLOAD_DIR = "solution_files"
if not os.path.exists(SOLUTION_UPLOAD_DIR):
    os.makedirs(SOLUTION_UPLOAD_DIR)

# Helper function to convert MongoDB ObjectId to string
def solution_helper(solution) -> dict:
    return {
        "id": str(solution["_id"]),
        "assignment_id": solution["assignment_id"],
        "answer_file": solution["answer_file"],
        "answered_by": solution["answered_by"],
        "submitted_on": solution["submitted_on"]
    }

# Create a new solution with file upload and form data
@router.post("/", response_model=Solution)
async def create_solution(
    current_user: dict = Depends(get_current_user),  # Get the current user
    assignment_id: str = Form(...),
    answer_file: Optional[List[UploadFile]] = File(None)
):
    if current_user["role"] not in ["helper", "admin"]:  # Helpers and Admins can post solutions
        raise HTTPException(status_code=403, detail="Only helpers and admins can post solutions.")
    
    file_paths = []
    
    # Save uploaded answer files and store their paths
    if answer_file:
        for file in answer_file:
            file_path = os.path.join(SOLUTION_UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            file_paths.append(file_path)  # Store file path

    # Build Solution instance using form data and saved file paths
    solution = Solution(
        assignment_id=assignment_id,
        answer_file=file_paths,
        answered_by=current_user["username"],  # Attach current user
        submitted_on=datetime.utcnow()
    )
    
    # Convert solution model to dict and insert into database
    solution_dict = solution.dict()
    new_solution = await solution_collection.insert_one(solution_dict)
    created_solution = await solution_collection.find_one({"_id": new_solution.inserted_id})

    return solution_helper(created_solution)

# Get all solutions for a particular assignment
@router.get("/assignment/{assignment_id}", response_model=List[Solution])
async def get_solutions_by_assignment(
    assignment_id: str,
    current_user: dict = Depends(get_current_user)  # Get the current user
):
    solutions = []
    # Students can see solutions only for assignments they posted
    if current_user["role"] == "student":
        assignments = await assignments.find({"created_by": current_user["username"], "_id": ObjectId(assignment_id)}).to_list(None)
        if not assignments:
            raise HTTPException(status_code=403, detail="You are not authorized to view solutions for this assignment.")
    
    async for solution in solution_collection.find({"assignment_id": assignment_id}):
        solutions.append(solution_helper(solution))
    
    return solutions

# Get a single solution by ID
@router.get("/{id}", response_model=Solution)
async def get_solution(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    solution = await solution_collection.find_one({"_id": ObjectId(id)})
    if solution is None:
        raise HTTPException(status_code=404, detail="Solution not found")
    return solution_helper(solution)

# Update a solution by ID (allows updating with new files)
@router.put("/{id}", response_model=Solution)
async def update_solution(
    id: str,
    current_user: dict = Depends(get_current_user),  # Get current user
    assignment_id: Optional[str] = Form(None),
    answer_file: Optional[List[UploadFile]] = File(None)
):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    solution_data = {}

    if assignment_id:
        solution_data["assignment_id"] = assignment_id
    
    # Save uploaded answer files if any
    if answer_file:
        solution_data["answer_file"] = []
        for file in answer_file:
            file_path = os.path.join(SOLUTION_UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            solution_data["answer_file"].append(file_path)

    # Update the solution in the database
    update_result = await solution_collection.update_one({"_id": ObjectId(id)}, {"$set": solution_data})
    
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    updated_solution = await solution_collection.find_one({"_id": ObjectId(id)})
    return solution_helper(updated_solution)

# Delete a solution by ID
@router.delete("/{id}")
async def delete_solution(id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":  # Only Admins can delete solutions
        raise HTTPException(status_code=403, detail="Only admins can delete solutions.")
    
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    delete_result = await solution_collection.delete_one({"_id": ObjectId(id)})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    return {"message": "Solution deleted successfully"}
