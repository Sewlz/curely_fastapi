from app.modules.user.repositories.user_repository import UserRepository
from app.modules.user.schemas.user_schema import UserCreate, UserUpdate

class UserService:
    @staticmethod
    def create_user(user_id: str, user_data: UserCreate):
        return UserRepository.add_user(user_id, user_data.dict())

    @staticmethod
    def update_user(user_id: str, update_data: UserUpdate):
        return UserRepository.update_user(user_id, update_data.dict(exclude_unset=True))

    @staticmethod
    def get_user(user_id: str):
        return UserRepository.get_user(user_id)
