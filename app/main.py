from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.modules.llm.controllers.llm_controller import router as llm_router
from app.modules.cnn.controllers.cnn_controller import router as cnn_router
from app.modules.user.controllers.user_controller import router as user_router
from app.modules.auth.controllers.auth_controller import router as auth_router
from app.modules.admin.controllers.admin_controller import router as admin_router

app = FastAPI(
    title="Curely FastAPI",
    description="Curely Backend Application Using FastAPI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/admins", tags=["Admin"])
app.include_router(auth_router, prefix="/auths", tags=["Auth"])
app.include_router(user_router, prefix="/users", tags=["User"])
app.include_router(cnn_router, prefix="/cnn", tags=["CNN"])
# app.include_router(llm_router, prefix="/llm", tags=["LLM"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Curely API"}