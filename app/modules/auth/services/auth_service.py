from supabase import create_client
from fastapi import HTTPException
from app.modules.auth.schemas.auth_schema import  LoginSchema
import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")  # Client API Key
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")


# Khởi tạo Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)  

class AuthService:
    @staticmethod
    def login_user(user_data: LoginSchema):
        """ Đăng nhập người dùng với Supabase và trả về access token và refresh token """
        
        # Thực hiện đăng nhập với Supabase (sử dụng sign_in_with_password thay cho sign_in)
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        # Kiểm tra lỗi từ Supabase
        if hasattr(response, "error") and response.error:  # Kiểm tra nếu có lỗi
            raise HTTPException(status_code=400, detail=response.error.message)
        
        # Kiểm tra nếu không có session hoặc access token
        if not response.session or not response.session.access_token or not response.session.refresh_token:
            raise HTTPException(status_code=400, detail="Failed to retrieve tokens after login")
        
        # Trả về thông tin người dùng và token
        user = response.user
        if not user or not user.id:
            raise HTTPException(status_code=400, detail="Failed to retrieve user information after login")


        return {
            "message": "User logged in successfully",
            "uid": user.id,  # Lấy id của người dùng
            "email": user.email,
            "role": "user",  # Thêm role vào đây
            "idToken": response.session.access_token,  # Access token
            "refreshToken": response.session.refresh_token  # Refresh token
        }