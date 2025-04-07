from app.common.database.supabasedb import supabase_db
from datetime import datetime, date
supabase_db = supabase_db()

class UserRepository:
    @staticmethod
    def add_user(user_id: str, user_data: dict):
        payload = {
            "userId": user_id,
            **{
                key: value.isoformat() if isinstance(value, datetime) else value
                for key, value in user_data.items()
            },
            "created_at": datetime.utcnow().isoformat()
        }

        res = supabase_db.table("users").insert(payload).execute()
        if res.data is None:
            raise Exception("Failed to insert user.")
        return {"message": "User added to database successfully"}

    @staticmethod
    def update_user(user_id: str, update_data: dict):
        payload = {
            **{
                key: (
                    value.isoformat()
                    if isinstance(value, (datetime, date)) else value
                )
                for key, value in update_data.items()
            },
            "created_at": datetime.utcnow().isoformat()  # cập nhật mỗi lần update
        }

        res = supabase_db.table("users").update(payload).eq("userId", user_id).execute()
        if res.data is None:
            raise Exception("Failed to update user.")
        return {"message": "User updated in database successfully"}

    @staticmethod
    def get_user(user_id: str):
        res = supabase_db.table("users").select("*").eq("userId", user_id).single().execute()
        if res.data is None:
            return None
        return res.data
