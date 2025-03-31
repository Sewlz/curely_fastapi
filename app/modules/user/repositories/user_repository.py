from app.common.database.firestore import db
from app.common.utils.encryption import aes_cipher

class UserRepository:
    COLLECTION_NAME = "users"

    @staticmethod
    def add_user(user_id: str, user_data: dict):
        encrypted_data = {key: aes_cipher.encrypt(value) for key, value in user_data.items()}
        db.collection(UserRepository.COLLECTION_NAME).document(user_id).set(encrypted_data)
        return {"message": "User added successfully"}

    @staticmethod
    def update_user(user_id: str, update_data: dict):
        encrypted_data = {key: aes_cipher.encrypt(value) for key, value in update_data.items()}
        db.collection(UserRepository.COLLECTION_NAME).document(user_id).update(encrypted_data)
        return {"message": "User updated successfully"}

    @staticmethod
    def get_user(user_id: str):
        user_ref = db.collection(UserRepository.COLLECTION_NAME).document(user_id).get()
        if user_ref.exists:
            decrypted_data = {key: aes_cipher.decrypt(value) for key, value in user_ref.to_dict().items()}
            return decrypted_data
        return None
