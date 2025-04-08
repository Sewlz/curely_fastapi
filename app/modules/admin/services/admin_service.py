from fastapi import HTTPException
from app.common.database.supabase import supabase


class AdminService:

    def promote_user_to_admin(user_id: str):
        try:
            # Cập nhật app_metadata để thay đổi quyền role thành 'admin'
            supabase.auth.admin.update_user_by_id(user_id, {
                "role": "admin"
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

