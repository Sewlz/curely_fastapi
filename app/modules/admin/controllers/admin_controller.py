import os
from app.common.security.auth import auth_guard
from app.common.database.supabase import supabaseAdmin
from fastapi import APIRouter, HTTPException, Depends, Request
from app.modules.admin.services.admin_service import AdminService
from app.common.security.admin import admin_guard  # đảm bảo đúng đường dẫn import

router = APIRouter()


@router.post("/promote_to_admin/{user_id}")
def promote_user(user_id: str, current_user=Depends(admin_guard)):
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required.")
    
    AdminService.promote_user_to_admin(user_id)

    return {"message": f"User {user_id} is now an admin."}

def sign_out_user():
    try:
        supabaseAdmin.auth.sign_out()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error signing out: {str(e)}")

@router.post("/sign_out")
async def sign_out(request: Request, user=Depends(auth_guard)):
    try:
        sign_out_user()
    except HTTPException as e:
        raise e
    
    return {"message": "User has been signed out successfully. Please remove tokens from client."}
