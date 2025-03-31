from firebase_admin import auth

class AdminService:
    @staticmethod
    def set_admin_role(user_id: str):
        """
        Cấp quyền admin cho user trong Firebase Authentication.
        """
        try:
            auth.set_custom_user_claims(user_id, {"role": "admin"})
            print(f"✅ User {user_id} đã được set lên admin.")
            return {"message": f"User {user_id} đã được set lên admin."}
        except Exception as e:
            print(f"❌ Lỗi khi set quyền admin: {str(e)}")
            raise Exception("Không thể set quyền admin.")


