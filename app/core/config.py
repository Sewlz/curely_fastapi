from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    # Cập nhật các biến môi trường với thông tin Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

    @property
    def supabase_credentials(self):
        # Trả về thông tin cấu hình Supabase dưới dạng một dict
        return {
            "url": self.SUPABASE_URL,
            "service_role_key": self.SUPABASE_SERVICE_ROLE_KEY,
            "jwt_secret": self.SUPABASE_JWT_SECRET
        }

# Khởi tạo Settings
settings = Settings()
