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
    def is_email_exist(email: str) -> bool:
        """
        Kiểm tra xem email đã tồn tại trong bảng users chưa
        """
        try:
            response = supabase_db.table("users").select("email").eq("email", email).single().execute()
            return bool(response.data)
        except Exception as e:
            print("🚨 Error checking email existence:", str(e))
            return False
    # @staticmethod
    # def upsert_oauth_user_data(user_data: dict):
    #     """
    #     Lưu hoặc cập nhật thông tin người dùng từ Google / Facebook
    #     """
    #     try:
    #         # Sử dụng Supabase để upsert (chèn hoặc cập nhật) dữ liệu vào bảng 'users'
    #         response = supabase_db.table("users") \
    #             .upsert(user_data, on_conflict=["userId"]) \
    #             .execute()

    #         # Kiểm tra kết quả từ Supabase
    #         if response.data:
    #             print("✅ User data upserted:", response.data)
    #         elif response.error:
    #             print("🚨 Error from Supabase:", response.error)
    #             raise HTTPException(status_code=500, detail="Error saving user data")
    #         else:
    #             print("🚨 Unexpected response:", response)
    #             raise HTTPException(status_code=500, detail="Unexpected error saving user data")

    #     except Exception as e:
    #         print("🚨 Error saving user data:", str(e))
    #         raise HTTPException(status_code=500, detail="Error saving user data")
    @staticmethod
    def upsert_oauth_user_data(user_id: str, user_data: dict):
        """
        Lưu hoặc chặn người dùng login Google nếu email đã tồn tại bằng phương thức khác.
        """
        try:
            # ❌ KHÔNG dùng .single() để tránh lỗi khi không có dòng nào
            response = supabase_db.table("users").select("*").eq("email", user_data["email"]).execute()

            # Nếu có user đã tồn tại với email này
            if response.data and len(response.data) > 0:
                existing = response.data[0]
                
                # Nếu userId khớp với userId Google => cho phép login
                if existing.get("userId") == user_id:
                    return {"status": "already_exists_google_user"}
                
                # Nếu không khớp => user này đăng ký bằng phương thức khác
                raise HTTPException(
                    status_code=400,
                    detail="This email is already registered with another method. Please log in using your password."
                )

            insert_response = supabase_db.table("users").insert(user_data).execute()

            # Kiểm tra nếu insert không thành công
            if not insert_response.data:
                raise HTTPException(status_code=500, detail="Failed to insert new Google user")

            return {"status": "inserted"}

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print("🚨 Exception in upsert_oauth_user_data:", str(e))
            raise HTTPException(status_code=500, detail="Internal Server Error")
