from fastapi import APIRouter, Depends, HTTPException 
from app.modules.admin.services.admin_service import AdminService
from app.common.security.admin import admin_guard
router = APIRouter()

@router.patch("/set-admin/{user_id}", tags=["Admin"])
def set_admin_role(
    user_id: str,
    admin_service: AdminService = Depends(),
    admin=Depends(admin_guard),  # ✅ Chỉ Admin mới có quyền gọi API này
):
    """
    API để cấp quyền admin cho user.
    """
    try:
        return admin_service.set_admin_role(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))