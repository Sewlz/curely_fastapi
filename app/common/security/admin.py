from fastapi import Request, HTTPException, Security, Depends
from app.common.security.auth import auth_guard  # Sử dụng auth_guard để xác thực user

async def admin_guard(request: Request, user=Depends(auth_guard)):
    """
    Kiểm tra xem user có quyền admin hay không.
    """
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")

    return user
