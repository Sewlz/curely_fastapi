import os
import uuid
import requests
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import id_token
from fastapi import HTTPException, Request
from app.common.database.supabase import supabase
from google.auth.transport.requests import Request 
from app.modules.auth.repositories.auth_repository import AuthRepository
from app.modules.auth.schemas.auth_schema import RegisterUserSchema, LoginSchema
from app.common.database.supabase import supabaseAdmin
load_dotenv()

CLIENT_ID_GOOGLE = os.getenv("CLIENT_ID_GOOGLE")
FACEBOOK_URL = os.getenv("FACEBOOK_URL")

class AuthService:
    @staticmethod
    def register_user(user_data: RegisterUserSchema):

        if user_data.password != user_data.confirm_password:
            raise HTTPException(status_code=400, detail="Password and confirm password do not match")

        # 🔍 Check email existence in the users table before registering
        if AuthRepository.is_email_exist(user_data.email):
            raise HTTPException(
                status_code=400,
                detail="This email is already registered with another method. Please log in using your password."
            )

        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })

        if hasattr(response, "error") and response.error:
            raise HTTPException(status_code=400, detail=response.error.message)

        user = response.user
        if not user or not user.id or not user.email:
            raise HTTPException(status_code=400, detail="Failed to retrieve user information after registration")

        user_data_to_insert = {
            "userId": user.id,
            "name": user_data.name,
            "email": user.email,
            "created_at": datetime.utcnow().isoformat(),
            "profilePicture": None
        }

        AuthRepository.insert_user_data(user_data_to_insert)

        return {
            "uid": user.id,
            "email": user.email,
        }

    @staticmethod
    def login_user(user_data: LoginSchema):
     
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
      
        if hasattr(response, "error") and response.error:
            raise HTTPException(status_code=400, detail=response.error.message)

        if not response.session or not response.session.access_token or not response.session.refresh_token:
            raise HTTPException(status_code=400, detail="Failed to retrieve tokens after login")
        
        user = response.user
        print('user', user)
        if not user or not user.id:
            raise HTTPException(status_code=400, detail="Failed to retrieve user information after login")


        return {
            "message": "User logged in successfully",
            "uid": user.id, 
            "email": user.email,
            "role": "user", 
            "idToken": response.session.access_token,  
            "refreshToken": response.session.refresh_token  
        }
    
    
    @staticmethod
    def refresh_token(refresh_token: str):
        try:
            session = supabase.auth.refresh_session(refresh_token)

            if not session or not session.session:
                raise HTTPException(status_code=400, detail="Invalid refresh token")

            return {
                "idToken": session.session.access_token,  
                "refreshToken": session.session.refresh_token,  
                "expiresIn": session.session.expires_in  
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    # @staticmethod
    # def login_with_google(id_token_str: str):
    #     try:
    #         idinfo = id_token.verify_oauth2_token(
    #             id_token_str,
    #             Request(),
    #             CLIENT_ID_GOOGLE
    #         )

    #         user_id = idinfo.get("sub")  
    #         email = idinfo.get("email")
    #         name = idinfo.get("name")
    #         picture = idinfo.get("picture")

    #         if not email:
    #             raise HTTPException(status_code=400, detail="Email not found in token")

    #         user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))

    #         user_data_to_insert = {
    #             "userId": user_uuid,
    #             "email": email,
    #         }

    #         AuthRepository.upsert_oauth_user_data(user_data_to_insert)

    #         return {
    #             "message": "User logged in successfully with Google",
    #             "uid": user_uuid,
    #             "email": email,
    #             "name": name,
    #             "picture": picture,
    #             "role": "user",
    #         }

    #     except ValueError as e:
    #         print("❌ Token verification failed:", str(e))
    #         raise HTTPException(status_code=401, detail="Invalid Google ID token")
    #     except Exception as e:
    #         print("🚨 Exception during login_with_google:", str(e))
    #         raise HTTPException(status_code=500, detail="Internal Server Error")
    # @staticmethod
    # def login_with_google(id_token_str: str):
    #     try:
    #         idinfo = id_token.verify_oauth2_token(
    #             id_token_str,
    #             Request(),
    #             CLIENT_ID_GOOGLE
    #         )

    #         user_id = idinfo.get("sub")
    #         email = idinfo.get("email")
    #         name = idinfo.get("name")
    #         picture = idinfo.get("picture")

    #         if not email:
    #             raise HTTPException(status_code=400, detail="Email not found in token")

    #         user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))

    #         user_data_to_insert = {
    #             "userId": user_uuid,
    #             "email": email,
    #             "name": name,
    #             "profilePicture": picture,
    #         }

    #         # Kiểm tra và xử lý insert hoặc từ chối login nếu trùng email
    #         result = AuthRepository.upsert_oauth_user_data(user_uuid, user_data_to_insert)

    #         if result.get("status") == "inserted":
    #             print(f"User {user_uuid} successfully inserted into users table.")

    #         return {
    #             "message": "User logged in successfully with Google",
    #             "uid": user_uuid,
    #             "email": email,
    #             "name": name,
    #             "picture": picture,
    #             "role": "user",
    #         }

    #     except HTTPException as http_exc:
    #         raise http_exc
    #     except ValueError as e:
    #         print("❌ Token verification failed:", str(e))
    #         raise HTTPException(status_code=401, detail="Invalid Google ID token")
    #     except Exception as e:
    #         print("🚨 Exception during login_with_google:", str(e))
    #         raise HTTPException(status_code=500, detail="Internal Server Error")
    def login_with_google(id_token: str):
        try:
            res = supabase.auth.sign_in_with_id_token({
                "provider": "google",
                "token": id_token
            })

            user = res.user
            user_metadata = user.user_metadata
            print("🧪 Supabase Response:", id_token)
            # Trích xuất thông tin cần thiết
            email = user.email
            name = user_metadata.get("full_name") or user_metadata.get("name")
            picture = user_metadata.get("avatar_url") or user_metadata.get("picture")
            user_uuid = user.id 
            access_token = res.session.access_token if res.session else None

            # ✅ Chuẩn bị dữ liệu để insert/check trong bảng users
            user_data_to_insert = {
                "userId": user_uuid,
                "email": email,
                "name": name,
                "profilePicture": picture,
            }

            # ✅ Gọi repository để xử lý insert/check
            insert_result = AuthRepository.upsert_oauth_user_data(user_uuid, user_data_to_insert)

            return {
                "email": email,
                "name": name,
                "picture": picture,
                "access_token": access_token,
                "status": insert_result["status"],
            }

        except HTTPException as http_exc:
            raise http_exc  # Cho phép FastAPI raise đúng lỗi
        except Exception as e:
            print("❌ Exception:", str(e))
            return {"error": str(e)}


        
    @staticmethod
    def login_with_facebook(id_token: str):
        try:
            print("📥 Received Facebook Access Token (id_token):", id_token)

            response = requests.get(
                FACEBOOK_URL,
                params={
                    "fields": "id,name,email,picture",
                    "access_token": id_token
                }
            )
            data = response.json()

            if "error" in data:
                print("❌ Facebook API error:", data["error"])
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
            print("🚨 Exception occurred during Facebook login:", str(e))
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
        
    # Hàm dăng xuất
    @staticmethod
    def sign_out_user_service():
        try:
            supabaseAdmin.auth.sign_out()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error signing out: {str(e)}")

