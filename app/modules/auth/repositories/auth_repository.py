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
            # Sử dụng Supabase để upsert (chèn hoặc cập nhật) dữ liệu vào bảng 'users'
            response = supabase_db.table("users") \
                .upsert(user_data, on_conflict=["userId"]) \
                .execute()

            # Kiểm tra kết quả từ Supabase
            if response.data:
                print("✅ User data upserted:", response.data)
            elif response.error:
                print("🚨 Error from Supabase:", response.error)
                raise HTTPException(status_code=500, detail="Error saving user data")
            else:
                print("🚨 Unexpected response:", response)
                raise HTTPException(status_code=500, detail="Unexpected error saving user data")

        except Exception as e:
            print("🚨 Error saving user data:", str(e))
            raise HTTPException(status_code=500, detail="Error saving user data")
