from fastapi import FastAPI
from routes.assignment import router as assignment_router
from routes.solution import router as solution_router
from routes.user import router as user_router
from routes.login import router as login_router  # Import login router

app = FastAPI()

# Include routers for different routes
app.include_router(assignment_router, prefix="/assignments", tags=["Assignments"])
app.include_router(solution_router, prefix="/solutions", tags=["Solutions"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(login_router, tags=["Authentication"])  # Include login router for auth
