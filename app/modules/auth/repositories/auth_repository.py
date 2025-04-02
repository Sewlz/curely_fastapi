from app.common.database.firestore import db
from datetime import datetime

class AuthRepository:
    COLLECTION_NAME = "users"

    @staticmethod
    def create_user(user_id: str, user_data: dict):
        """
        Lưu thông tin người dùng vào Firestore sau khi đăng ký.
        """
        user_data["createdAt"] = datetime.utcnow().isoformat()  # Lưu thời gian tạo dưới dạng chuỗi
        db.collection(AuthRepository.COLLECTION_NAME).document(user_id).set(user_data)
        return {"message": "User added successfully"}

    @staticmethod
    def update_user(user_id: str, update_data: dict):
        """
        Cập nhật thông tin người dùng trong Firestore.
        """
        db.collection(AuthRepository.COLLECTION_NAME).document(user_id).update(update_data)
        return {"message": "User updated successfully"}

    @staticmethod
    def get_user(user_id: str):
        """
        Lấy thông tin người dùng từ Firestore.
        """
        user_ref = db.collection(AuthRepository.COLLECTION_NAME).document(user_id).get()
        if user_ref.exists:
            return user_ref.to_dict()
        return None
