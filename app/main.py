from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.auth.controllers.auth_controller import router as auth_router
from app.modules.cnn.controllers.cnn_controller import router as cnn_router
from app.modules.llm.controllers.llm_controller import router as llm_router

app = FastAPI(
    title="Curely FastAPI",
    description="Curely Backend Application Using FastAPI",
    version="1.0.0",
)

# CORS Middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from modules
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(cnn_router, prefix="/cnn", tags=["CNN"])
app.include_router(llm_router, prefix="/llm", tags=["LLM"])

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Curely API"}