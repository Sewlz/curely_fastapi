from fastapi import APIRouter, HTTPException
from app.modules.user.services.user_service import UserService
from app.modules.user.schemas.user_schema import UserCreate, UserUpdate

router = APIRouter()

@router.post("/{user_id}", response_model=dict)
def create_user(user_id: str, user_data: UserCreate):
    try:
        return UserService.create_user(user_id, user_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}", response_model=dict)
def update_user(user_id: str, update_data: UserUpdate):
    try:
        return UserService.update_user(user_id, update_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=dict)
def get_user(user_id: str):
    try:
        user = UserService.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
