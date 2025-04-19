from fastapi import APIRouter, Depends, HTTPException, requests
from fastapi.security import HTTPBearer
from app.modules.auth.schemas.auth_schema import RegisterUserSchema, LoginSchema , GoogleLoginSchema ,ForgotPasswordSchema ,FacebookLoginSchema
from app.modules.auth.services.auth_service import AuthService
router = APIRouter()
security = HTTPBearer()

# from app.common.security.auth import auth_guard
# from app.modules.auth.repositories.auth_repository import AuthRepository

# Đăng ký người dùng

@router.post("/register")
def register_user(user_data: RegisterUserSchema, auth_service: AuthService = Depends(AuthService)):
    try:
        # Gọi phương thức đăng ký người dùng từ AuthService
        result = auth_service.register_user(user_data)
        
        # Nếu kết quả không trả về thông tin người dùng, tức là có lỗi
        if not result:
            raise HTTPException(status_code=400, detail="Registration failed")
        
        # Trả về thông tin người dùng đã đăng ký thành công
        return {
            "message": "User registered successfully",
            "uid": result["uid"],
            "email": result["email"],

        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



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
    
# Refresh_token người dùng 
@router.post("/refresh-token")
def refresh_token(refresh_token: str, auth_service: AuthService = Depends()):
    result = auth_service.refresh_token(refresh_token)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    return {
        "message": "Token refreshed successfully",
        "idToken": result["idToken"],
        "refreshToken": result["refreshToken"],
        "expiresIn": result["expiresIn"]
    }


   
@router.post("/login-google")
def login_google(payload: GoogleLoginSchema, auth_service: AuthService = Depends()):
    print(f"Received payload: {payload}")  # ✅ In ra log kiểm tra payload
    result = auth_service.login_with_google(payload.id_token)
    if not result:
        raise HTTPException(status_code=400, detail="Google login failed")
    return result


@router.post("/login-facebook")
def login_with_facebook(payload: FacebookLoginSchema):
    try:
        return AuthService.login_with_facebook(payload.id_token)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong while logging in with Facebook")
    
    

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordSchema, auth_service: AuthService = Depends()):
    return auth_service.forgot_password(payload.email)
