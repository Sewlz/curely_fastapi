from fastapi import APIRouter, HTTPException, Depends, Request
from supabase import create_client
import os
from app.common.security.auth import auth_guard  # Bảo vệ route
from app.modules.user.repositories.user_repository import UserRepository
# Cấu hình URL và key từ biến môi trường hoặc trực tiếp
SUPABASE_URL = os.getenv("SUPABASE_URL")  # Hoặc đặt giá trị trực tiếp
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Hoặc đặt giá trị trực tiếp

# Tạo client Supabase
supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

from fastapi import APIRouter, HTTPException

router = APIRouter()

# Hàm để promote user thành admin
def promote_user_to_admin(user_id: str):
    try:
        # Cập nhật app_metadata để thay đổi quyền role thành 'admin'
        supabase.auth.admin.update_user_by_id(user_id, {
            "role": "admin" 
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API endpoint để promote user thành admin
@router.post("/promote_to_admin/{user_id}")
def promote_user(user_id: str):
    # Kiểm tra user_id trước (ví dụ validate)
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required.")
    
    # Gọi hàm promote
    promote_user_to_admin(user_id)

    return {"message": f"User {user_id} is now an admin."}


# Hàm để đăng xuất (sign out)
def sign_out_user():
    try:
        # Xóa phiên làm việc của người dùng, tức là hủy token đang sử dụng
        supabase.auth.sign_out()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error signing out: {str(e)}")

# API endpoint để đăng xuất người dùng
@router.post("/sign_out")
async def sign_out(request: Request, user=Depends(auth_guard)):
    try:
        # Gọi hàm đăng xuất
        sign_out_user()
    except HTTPException as e:
        raise e
    
    return {"message": "User has been signed out successfully. Please remove tokens from client."}
