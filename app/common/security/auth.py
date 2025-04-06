from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
import os
from dotenv import load_dotenv
import jwt

# Load biến môi trường
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Tạo Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

security = HTTPBearer()

class AuthGuard:
    async def __call__(self, request: Request, credentials: HTTPAuthorizationCredentials = Security(security)):
        if not credentials:
            raise HTTPException(status_code=401, detail="No token provided")

        token = credentials.credentials

        try:
            # Giải mã JWT từ Supabase (dùng JWT decode để lấy payload)
            payload = jwt.decode(token, options={"verify_signature": False})  # KHÔNG dùng verify_signature trên client
            user_id = payload.get("sub")
            role = payload.get("role", "user")

            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token payload")

            # In ra thông tin người dùng trên console
            print(f"Authenticated User ID: {user_id}, Role: {role}")

            # Thêm thông tin người dùng vào request.state
            request.state.user = {"uid": user_id, "role": role}

            # Trả về thông tin người dùng
            return {"uid": user_id, "role": role}

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

auth_guard = AuthGuard()
