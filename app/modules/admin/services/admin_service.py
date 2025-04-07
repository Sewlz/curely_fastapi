from fastapi import HTTPException
from supabase import create_client
import os
# Cấu hình URL và key từ biến môi trường hoặc trực tiếp
SUPABASE_URL = os.getenv("SUPABASE_URL")  # Hoặc đặt giá trị trực tiếp
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Hoặc đặt giá trị trực tiếp

# Tạo client Supabase
supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)


class AdminService:

    def promote_user_to_admin(user_id: str):
        try:
            # Cập nhật app_metadata để thay đổi quyền role thành 'admin'
            supabase.auth.admin.update_user_by_id(user_id, {
                "role": "admin"
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

