from fastapi import Response
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
