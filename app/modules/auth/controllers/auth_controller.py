from fastapi import APIRouter, Depends, HTTPException
from app.modules.auth.schemas.auth_schema import RegisterUserSchema, LoginSchema , GoogleLoginSchema ,FacebookLoginSchema , ForgotPasswordSchema
from app.modules.auth.services.auth_service import AuthService
router = APIRouter()

@router.post("/register", tags=["Auth"])
def register_user(user_data: RegisterUserSchema, auth_service: AuthService = Depends()):
    result = auth_service.register_user(user_data)
    if not result:
        raise HTTPException(status_code=400, detail="Registration failed")
    return {
        "message": "User registered successfully",
        "uid": result["uid"],
        "email": result["email"],
        "role": result["role"]
    }

@router.post("/login", tags=["Auth"])
def login(user_data: LoginSchema, auth_service: AuthService = Depends()):
    result = auth_service.login_user(user_data)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {
        "message": "Login successful",
        "idToken": result["idToken"],
        "refreshToken": result["refreshToken"],
        "role": result["role"],
        "expiresIn": result["expiresIn"]
    }

@router.post("/login-google", tags=["Auth"])
def login_google(payload: GoogleLoginSchema, auth_service: AuthService = Depends()):
    """
    API để đăng nhập bằng Google.
    """
    print(f"Received payload: {payload}")  # ✅ In ra log kiểm tra payload
    result = auth_service.login_with_google(payload.id_token)
    if not result:
        raise HTTPException(status_code=400, detail="Google login failed")
    return result

@router.post("/login-facebook", tags=["Auth"])
def login_facebook(payload: FacebookLoginSchema, auth_service: AuthService = Depends()):
    """
    API để đăng nhập bằng Facebook.
    """
    print(f"Received payload: {payload}")  # ✅ Log kiểm tra payload
    result = auth_service.login_with_facebook(payload.id_token)
    if not result:
        raise HTTPException(status_code=400, detail="Facebook login failed")
    return result

@router.post("/refresh-token", tags=["Auth"])
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

@router.post("/forgot-password", tags=["Auth"])
def forgot_password(payload: ForgotPasswordSchema, auth_service: AuthService = Depends()):
    return auth_service.forgot_password(payload.email)