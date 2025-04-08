import os
from fastapi import HTTPException
from supabase import create_client
from app.modules.user.repositories.user_repository import UserRepository
from app.modules.user.schemas.user_schema import UserCreate, UserUpdate
# Cấu hình URL và key từ biến môi trường hoặc trực tiếp
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


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
    @staticmethod
    def update_password(uid: str, email: str, current_password: str, new_password: str):
        if not email:
            raise HTTPException(status_code=400, detail="Email not found in token.")

        if not current_password or not new_password:
            raise HTTPException(status_code=400, detail="Current and new passwords are required.")

        # ✅ 1. Xác thực mật khẩu hiện tại
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": current_password
            })

            # Check kỹ hơn
            if not auth_response or not getattr(auth_response, "user", None):
                print("❌ Invalid current password (no user returned)")
                raise HTTPException(status_code=401, detail="Current password is incorrect.")

        except Exception as e:
            print(f"❌ Exception while verifying current password: {e}")
            if "Invalid login credentials" in str(e):
                raise HTTPException(status_code=401, detail="Current password is incorrect.")
            # Nếu message từ Supabase có nội dung, trả về luôn để debug dễ
            if hasattr(e, "message"):
                raise HTTPException(status_code=401, detail=str(e.message))
            raise HTTPException(status_code=401, detail="Current password is incorrect.")

        # ✅ 2. Đổi mật khẩu mới bằng auth client
        try:
            response = supabase.auth.update_user({"password": new_password})
        except Exception as e:
            print(f"❌ Supabase update error: {e}")
            raise HTTPException(status_code=500, detail="Failed to update password.")

        return {"message": "Password updated successfully."}
        
    # Hàm để xóa người dùng
    def delete_user(user_id: str):
        try:
            # Xóa dữ liệu người dùng khỏi cơ sở dữ liệu
            UserRepository.delete_user(user_id)
            
            # Xóa user khỏi Supabase Authentication
            supabase.auth.admin.delete_user(user_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
                   

                   