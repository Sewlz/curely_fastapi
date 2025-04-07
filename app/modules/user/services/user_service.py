import os
from fastapi import HTTPException
from supabase import create_client
from app.modules.user.repositories.user_repository import UserRepository
from app.modules.user.schemas.user_schema import UserCreate, UserUpdate
# Cấu hình URL và key từ biến môi trường hoặc trực tiếp
SUPABASE_URL = os.getenv("SUPABASE_URL")  # Hoặc đặt giá trị trực tiếp
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Hoặc đặt giá trị trực tiếp

# Tạo client Supabase
supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

class UserService:
    @staticmethod
    def create_user(user_id: str, user_data: UserCreate):
        return UserRepository.add_user(user_id, user_data.dict(exclude_unset=True))

    @staticmethod
    def update_user(user_id: str, update_data: UserUpdate):
        return UserRepository.update_user(user_id, update_data.dict(exclude_unset=True))

    @staticmethod
    def get_user(user_id: str):
        return UserRepository.get_user(user_id)
    
        
    # Hàm để thay đổi mật khẩu người dùng
    def update_user_password(user_id: str, new_password: str):
        try:
            # Cập nhật mật khẩu mới cho người dùng trong Supabase
            supabase.auth.admin.update_user_by_id(user_id, {
                "password": new_password
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating password: {str(e)}")
        
    # Hàm để xóa người dùng
    def delete_user(user_id: str):
        try:
            # Xóa dữ liệu người dùng khỏi cơ sở dữ liệu
            UserRepository.delete_user(user_id)
            
            # Xóa user khỏi Supabase Authentication
            supabase.auth.admin.delete_user(user_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
                   