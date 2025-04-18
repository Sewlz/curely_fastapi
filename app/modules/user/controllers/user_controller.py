from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from app.modules.user.services.user_service import UserService 
from app.modules.user.schemas.user_schema import UserCreate, UserUpdate ,UpdatePasswordSchema
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
        user_id = request.state.user.get("uid")
        user_data = UserService.get_user(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        return user_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/update-profile-picture", response_model=dict)
async def update_profile_picture(
    request: Request,
    image: UploadFile = File(...),
    user=Depends(auth_guard)
):
    try:
        user_id = request.state.user.get("uid")
        return UserService.update_profile_picture(user_id, image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/update_password", response_model=dict)
def update_password(
    request: Request,
    data: UpdatePasswordSchema,
    user = Depends(auth_guard), 
):
    try:
        uid = request.state.user.get("uid")
        email = request.state.user.get("email")

        print(f"🔍 DEBUG - UID: {uid}")
        print(f"🔍 DEBUG - Email: {email}")

        if not uid or not email:
            raise HTTPException(status_code=400, detail="User info missing from token.")

        return UserService.update_password(
            uid=uid,
            email=email,
            current_password=data.current_password,
            new_password=data.new_password,
        )        
    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        # ❌ Chỉ bắt lỗi không rõ nguyên nhân
        print(f"❌ Unexpected error in update_password: {str(e)}")
        raise HTTPException(status_code=500, detail="Something went wrong while updating password.")


# API endpoint để xóa người dùng
@router.delete("/delete_user", response_model=dict)
async def delete_user_account(request: Request, user=Depends(auth_guard)):
    # Lấy user_id từ token đã được xác thực qua request.state.user
    user_id = request.state.user.get("uid")  # Lấy uid từ token
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token.")
    
    try:
        # Gọi hàm delete từ UserService
        UserService.delete_user(user_id)
    except HTTPException as e:
        raise e
    
    return {"message": f"User {user_id} has been deleted."}
