from app.common.database.firestore import db
from app.common.utils.encryption import aes_cipher
from datetime import datetime

class AuthRepository:
    COLLECTION_NAME = "users"

    @staticmethod
    def create_user(user_id: str, user_data: dict):
        """
        Lưu thông tin người dùng vào Firestore sau khi đăng ký.
        - Mã hóa tất cả thông tin trước khi lưu vào Firestore.
        """

        # Mã hóa tất cả dữ liệu trước khi lưu vào Firestore
        encrypted_data = {key: aes_cipher.encrypt(value) for key, value in user_data.items()}
        encrypted_data["createdAt"] = aes_cipher.encrypt(datetime.utcnow().isoformat())  # Mã hóa thời gian tạo
        
        # Lưu dữ liệu vào Firestore
        db.collection(AuthRepository.COLLECTION_NAME).document(user_id).set(encrypted_data)
        return {"message": "User added successfully"}

    @staticmethod
    def update_user(user_id: str, update_data: dict):
        """
        Dữ liệu sẽ được mã hóa trước khi lưu trữ.
        """

        # Mã hóa dữ liệu update
        encrypted_data = {key: aes_cipher.encrypt(value) for key, value in update_data.items()}
        db.collection(AuthRepository.COLLECTION_NAME).document(user_id).update(encrypted_data)
        return {"message": "User updated successfully"}

    @staticmethod
    def get_user(user_id: str):
        """
        Lấy thông tin người dùng từ Firestore, giải mã dữ liệu trước khi trả về.
        """
        user_ref = db.collection(AuthRepository.COLLECTION_NAME).document(user_id).get()
        if user_ref.exists:
            decrypted_data = {key: aes_cipher.decrypt(value) for key, value in user_ref.to_dict().items()}
            return decrypted_data
        return None
