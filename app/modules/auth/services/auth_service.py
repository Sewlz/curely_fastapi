from supabase import create_client
from fastapi import HTTPException, Request
from app.modules.auth.repositories.auth_repository import AuthRepository
from app.modules.auth.schemas.auth_schema import RegisterUserSchema, LoginSchema
import os
from dotenv import load_dotenv
from datetime import datetime

# Load biến môi trường từ file .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")  # Client API Key
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")


# Khởi tạo Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

class AuthService:
    @staticmethod
    def register_user(user_data: RegisterUserSchema):
        """ Đăng ký người dùng với Supabase Auth và lưu thông tin vào bảng users """

        if user_data.password != user_data.confirm_password:
            raise HTTPException(status_code=400, detail="Password and confirm password do not match")

        # Đăng ký trên Auth
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })

        if hasattr(response, "error") and response.error:
            raise HTTPException(status_code=400, detail=response.error.message)

        user = response.user
        if not user or not user.id or not user.email:
            raise HTTPException(status_code=400, detail="Failed to retrieve user information after registration")

        # Lưu vào bảng users bằng repository
        user_data_to_insert = {
            "userId": user.id,
            "name": user_data.name,
            "email": user.email,
            "created_at": datetime.utcnow().isoformat(),
            "profilePicture": None  # để trống, cập nhật sau
        }
        AuthRepository.insert_user_data(user_data_to_insert)

        return {
            "uid": user.id,
            "email": user.email,
        }

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
    
    
    @staticmethod
    def refresh_token(refresh_token: str):
        """ Làm mới token bằng Supabase """
        try:
            session = supabase.auth.refresh_session(refresh_token)

            if not session or not session.session:
                raise HTTPException(status_code=400, detail="Invalid refresh token")

            return {
                "idToken": session.session.access_token,  # Token mới
                "refreshToken": session.session.refresh_token,  # Refresh token mới
                "expiresIn": session.session.expires_in  # Thời gian hết hạn
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    

    @staticmethod
    def login_with_google(id_token: str):
        """ Xác thực người dùng qua Google ID token """
        
        try:
            # Gửi ID token lên Supabase để xác thực
            response = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "id_token": id_token
            })
            
            # Kiểm tra lỗi từ Supabase
            if hasattr(response, "error") and response.error:
                raise HTTPException(status_code=400, detail=response.error.message)
            
            # Nếu không có session hoặc access token, báo lỗi
            if not response.session or not response.session.access_token:
                raise HTTPException(status_code=400, detail="Failed to retrieve tokens after Google login")
            
            # Trả về thông tin người dùng và token
            user = response.user
            return {
                "message": "User logged in successfully",
                "uid": user.id,
                "email": user.email,
                "role": "user",
                "idToken": response.session.access_token,  # Access token
                "refreshToken": response.session.refresh_token  # Refresh token
            }
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    def forgot_password(email: str):
        try:
            response = supabase.auth.reset_password_email(email)
            if hasattr(response, "error") and response.error:
                raise HTTPException(status_code=400, detail=response.error.message)
            return {"message": "Password reset email sent successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

