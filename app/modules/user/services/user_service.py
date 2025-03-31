import os
import firebase_admin
from firebase_admin import auth
from fastapi import HTTPException
import requests
from app.modules.user.repositories.user_repository import UserRepository
from app.modules.user.schemas.user_schema import UserCreate, UserUpdate


API_KEY = os.getenv("APIKEY")

class UserService:
    @staticmethod
    def resend_verification_email(email: str):
        try:
            # ✅ Kiểm tra user có tồn tại không
            try:
                user = auth.get_user_by_email(email)
            except firebase_admin.auth.UserNotFoundError:
                raise HTTPException(status_code=404, detail="Email không tồn tại trong hệ thống.")

            # ✅ Kiểm tra email đã xác minh chưa
            if user.email_verified:
                return {"message": "Email đã được xác minh, không cần gửi lại."}

            # 🔥 Gửi lại email xác minh
            verification_link = auth.generate_email_verification_link(email)

            return {
                "message": "Đã gửi lại email xác minh.",
                "verification_link": verification_link
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    

    @staticmethod
    def revoke_user_tokens(user_id: str):
        """
        Thu hồi refresh token của người dùng, yêu cầu họ phải đăng nhập lại.
        """
        try:
            auth.revoke_refresh_tokens(user_id)
            print(f"Refresh tokens của user {user_id} đã bị thu hồi.")
        except Exception as e:
            print("Lỗi khi thu hồi refresh token:", e)
            raise HTTPException(status_code=500, detail="Failed to revoke refresh token")
        
    @staticmethod
    def delete_user(user_id: str):
        """
        Xóa tài khoản người dùng trên Firebase Authentication.
        """
        try:
            auth.delete_user(user_id)
            print(f"✅ User {user_id} đã bị xóa thành công.")
            return {"message": f"User {user_id} đã bị xóa thành công."}
        except Exception as e:
            print(f"❌ Lỗi khi xóa user {user_id}: {str(e)}")
            raise Exception("Không thể xóa người dùng.") 


    @staticmethod   
    def change_password(user_id: str, payload):
        old_password = payload.old_password
        new_password = payload.new_password
        confirm_password = payload.confirm_password

        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="Mật khẩu xác nhận không khớp")

        try:
            # Lấy thông tin user từ Firebase
            user = auth.get_user(user_id)
            if not user.email:
                raise HTTPException(status_code=400, detail="Không tìm thấy email của người dùng.")

            # Xác thực mật khẩu cũ bằng cách đăng nhập
            login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
            login_payload = {
                "email": user.email,
                "password": old_password,
                "returnSecureToken": True
            }

            response = requests.post(login_url, json=login_payload)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Mật khẩu cũ không chính xác.")

            # Cập nhật mật khẩu mới
            auth.update_user(user_id, password=new_password)
            return {"message": "Đổi mật khẩu thành công"}

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        


    @staticmethod
    def create_user(user_id: str, user_data: UserCreate):
        return UserRepository.add_user(user_id, user_data.dict())

    @staticmethod
    def update_user(user_id: str, update_data: UserUpdate):
        return UserRepository.update_user(user_id, update_data.dict(exclude_unset=True))

    @staticmethod
    def get_user(user_id: str):
        return UserRepository.get_user(user_id)
