from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers từ modules
from app.modules.user.controllers.user_controller import router as user_router

app = FastAPI(
    title="User Management API",
    description="API for managing users with AES encryption",
    version="1.0.0",
)

# CORS Middleware để frontend có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Đổi lại trong production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router từ module User
app.include_router(user_router, prefix="/users", tags=["User"])

# Root API test
@app.get("/")
def read_root():
    return {"message": "Welcome to User Management API"}

# Chạy bằng: uvicorn app.main:app --reload
