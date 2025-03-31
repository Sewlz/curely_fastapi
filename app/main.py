from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers from modules
from app.modules.auth.controllers.auth_controller import router as auth_router

app = FastAPI(
    title="FastAPI Modular Monolith",
    description="A modular monolith FastAPI project with structured architecture.",
    version="1.0.0",
)

# CORS Middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from modules
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Modular Monolith API"}

# Run using: uvicorn app.main:app --reload