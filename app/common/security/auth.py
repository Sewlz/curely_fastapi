from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import jwt

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
            email = payload.get("email") 

            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token payload")

            # In ra thông tin người dùng trên console
            print(f"Authenticated User ID: {user_id}, Role: {role}, email: {email}" )

            # Thêm thông tin người dùng vào request.state
            request.state.user = {"uid": user_id, "role": role,  "email": email}



            # Trả về thông tin người dùng
            return {"uid": user_id, "role": role, "email": email}

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

auth_guard = AuthGuard()
