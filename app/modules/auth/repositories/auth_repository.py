from fastapi import HTTPException, Response
from app.common.database.supabase import supabase
supabase_db = supabase
class AuthRepository:
    @staticmethod
    def insert_user_data(user_data: dict):
        """
        Hàm lưu thông tin người dùng vào bảng users
        """
        try:
            # Gửi yêu cầu insert dữ liệu vào Supabase
           supabase_db.table("users").insert(user_data).execute()
        except Exception as e:
            raise Exception(f"Error saving user data: {str(e)}")
        
    @staticmethod
    def upsert_oauth_user_data(user_data: dict):
        """
        Lưu hoặc cập nhật thông tin người dùng từ Google / Facebook
        """
        try:
            response = supabase_db.table("users") \
                .upsert(user_data, on_conflict="userId") \
                .execute()
            print("✅ User data upserted:", response)
        except Exception as e:
            print("🚨 Error saving user data:", str(e))
            raise HTTPException(status_code=500, detail="Error saving user data")