from fastapi import HTTPException, Request
from app.modules.auth.repositories.auth_repository import AuthRepository
from app.modules.auth.schemas.auth_schema import RegisterUserSchema, LoginSchema
from datetime import datetime
from app.common.database.supabase import supabase
from google.oauth2 import id_token
from google.auth.transport.requests import Request 
import requests
import uuid
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
    def login_with_google(id_token_str: str):
        try:
            # ✅ Xác minh ID token với Google
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                Request(),
                "463830006871-2m8oc6d00tnne7p63g61ggd442t9upi2.apps.googleusercontent.com"
            )

            # ✅ Trích xuất thông tin người dùng
            user_id = idinfo.get("sub")  # Google user ID (not UUID)
            email = idinfo.get("email")
            name = idinfo.get("name")
            picture = idinfo.get("picture")

            if not email:
                raise HTTPException(status_code=400, detail="Email not found in token")

            # ✅ Tạo UUID từ user_id của Google (đảm bảo UUID duy nhất và cố định cho user)
            user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))

            # ✅ Chuẩn bị dữ liệu để lưu vào Supabase
            user_data_to_insert = {
                "userId": user_uuid,  # Sử dụng UUID cố định thay vì user_id
                "email": email,
            }

            # ✅ Lưu vào DB (upsert)
            AuthRepository.upsert_oauth_user_data(user_data_to_insert)

            return {
                "message": "User logged in successfully with Google",
                "uid": user_uuid,
                "email": email,
                "name": name,
                "picture": picture,
                "role": "user",
            }

        except ValueError as e:
            print("❌ Token verification failed:", str(e))
            raise HTTPException(status_code=401, detail="Invalid Google ID token")
        except Exception as e:
            print("🚨 Exception during login_with_google:", str(e))
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    @staticmethod
    def login_with_facebook(id_token: str):
        try:
            # 👇 Log token nhận được từ frontend
            print("📥 Received Facebook Access Token (id_token):", id_token)

            response = requests.get(
                "https://graph.facebook.com/me",
                params={
                    "fields": "id,name,email,picture",
                    "access_token": id_token
                }
            )
            data = response.json()

            if "error" in data:
                print("❌ Facebook API error:", data["error"])  # 👈 log lỗi rõ ràng
                raise HTTPException(status_code=401, detail="Invalid Facebook access token")

            user_id = data.get("id")
            name = data.get("name")
            email = data.get("email")
            picture = data.get("picture", {}).get("data", {}).get("url")

            return {
                "message": "User logged in successfully with Facebook",
                "uid": user_id,
                "email": email,
                "name": name,
                "picture": picture,
                "role": "user"
            }

        except Exception as e:
            print("🚨 Exception occurred during Facebook login:", str(e))  # 👈 debug exception
            raise HTTPException(status_code=500, detail="Error verifying Facebook token")

    
    @staticmethod
    def forgot_password(email: str):
        try:
            response = supabase.auth.reset_password_email(email)
            if hasattr(response, "error") and response.error:
                raise HTTPException(status_code=400, detail=response.error.message)
            return {"message": "Password reset email sent successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

