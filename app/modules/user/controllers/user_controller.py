from fastapi import APIRouter, HTTPException, Depends, Request
from app.modules.user.services.user_service import UserService
from app.modules.user.schemas.user_schema import UserCreate, UserUpdate
from app.common.security.auth import auth_guard  # Bảo vệ route

router = APIRouter()

@router.post("/{user_id}", response_model=dict)
async def create_user(
    user_id: str,
    user_data: UserCreate,
    request: Request,
    user=Depends(auth_guard)
):
    try:
        return UserService.create_user(user_id, user_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/update-user", response_model=dict)
async def update_user(
    update_data: UserUpdate,
    request: Request,
    user=Depends(auth_guard)
):
    try:
        # Lấy user_id từ token
        user_id = request.state.user.get("uid")
        return UserService.update_user(user_id, update_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/get-user", response_model=dict)
async def get_user(
    request: Request,
    user=Depends(auth_guard)
):
    try:
        # Lấy user_id từ token
        user_id = request.state.user.get("uid")
        user_data = UserService.get_user(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        return user_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
