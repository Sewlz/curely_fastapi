from fastapi import APIRouter, Depends, HTTPException, requests
from fastapi.security import HTTPBearer
from app.modules.auth.schemas.auth_schema import LoginSchema 
from app.modules.auth.services.auth_service import AuthService
router = APIRouter()
security = HTTPBearer()



# email: nhut@gmail.com
# password: Nhut1234


# Đăng nhập người dùng
@router.post("/login")
def login_user(user_data: LoginSchema, auth_service: AuthService = Depends(AuthService)):
    try:
        # Gọi phương thức đăng nhập người dùng từ AuthService
        result = auth_service.login_user(user_data)
        
        # Nếu không có kết quả từ đăng nhập, tức là có lỗi
        if not result:
            raise HTTPException(status_code=400, detail="Login failed")
        
        # Trả về thông tin người dùng đã đăng nhập thành công
        return {
            "message": "User logged in successfully",
            "uid": result["uid"],
            "email": result["email"],
            "role": result["role"],
            "idToken":result["idToken"],
            "refreshToken" : result["refreshToken"]
        }
    
    except HTTPException as e:
        # Nếu có lỗi từ phía AuthService, trả về lỗi đó
        raise e
    except Exception as e:
        # Bắt mọi lỗi khác và trả về lỗi server
        raise HTTPException(status_code=500, detail=str(e))