from fastapi import APIRouter, HTTPException
from app.modules.user.services.user_service import UserService
from app.modules.user.schemas.user_schema import UserCreate, UserUpdate

router = APIRouter()

@router.post("/{user_id}", response_model=dict)
def create_user(user_id: str, user_data: UserCreate):
    return UserService.create_user(user_id, user_data)

@router.put("/{user_id}", response_model=dict)
def update_user(user_id: str, update_data: UserUpdate):
    return UserService.update_user(user_id, update_data)

@router.get("/{user_id}", response_model=dict)
def get_user(user_id: str):
    user = UserService.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
