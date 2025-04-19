from fastapi import HTTPException
from app.common.database.supabase import supabaseAdmin

class AdminService:
    def promote_user_to_admin(user_id: str):
        try:
            supabaseAdmin.auth.admin.update_user_by_id(user_id, {
                "role": "admin"
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

