from fastapi import APIRouter, Depends, HTTPException, Request
from app.modules.user.services.user_service import UserService
from app.modules.user.schemas.user_schema import UserCreate, UserUpdate , ChangePasswordSchema
from app.common.security.auth_guard import auth_guard
router = APIRouter()

@router.post("/resend-verification-email", tags=["User"])
def resend_verification(email: str, user_service: UserService = Depends()):
    result = user_service.resend_verification_email(email)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to resend verification email")
    return result

@router.get("/check-role", tags=["User"])
def check_user_role(request: Request, user=Depends(auth_guard)):
    """
    API trả về role của user sau khi đã xác thực
    """
    return {"uid": user.get("uid"), "role": user.get("role")}

@router.post("/logout", tags=["User"])
def logout(request: Request, user_service: UserService = Depends(), user=Depends(auth_guard)):
    """
    API để user logout, thu hồi refresh token của họ.
    """
    user_id = user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        user_service.revoke_user_tokens(user_id)
        return {"message": "User logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/change-password", tags=["User"])
def change_password(
    request: Request,
    payload: ChangePasswordSchema,
    user_service: UserService = Depends(),
    user=Depends(auth_guard)
):
    user_id = user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    return user_service.change_password(user_id, payload)

@router.delete("/delete-account", tags=["User"])
def delete_account(request: Request, user_service: UserService = Depends(), user=Depends(auth_guard)):
    """
    API xóa tài khoản người dùng sau khi đã xác thực.
    """
    user_id = user.get("uid")

    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        user_service.delete_user(user_id)  # ✅ Gọi hàm trong service để xử lý
        return {"message": f"User {user_id} đã bị xóa thành công."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể xóa người dùng: {str(e)}")
    

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
