# from fastapi import APIRouter, FastAPI, HTTPException, Depends
# from fastapi.security import HTTPBearer
# from pydantic import BaseModel
# import supabase
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Tải thông tin từ file .env
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")  # Chú ý: Dùng Supabase service_role key khi truy cập các API yêu cầu quyền cao hơn
# SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# # Khởi tạo Supabase client
# supabase = supabase.create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# # Khởi tạo FastAPI và HTTPBearer
# # Khởi tạo FastAPI và HTTPBearer
# router = APIRouter()

# security = HTTPBearer()

# # Pydantic model để yêu cầu cập nhật mật khẩu
# class UpdatePasswordRequest(BaseModel):
#     new_password: str

# # Route cập nhật mật khẩu
# @router.post("/update-password")
# async def update_password(
#     body: UpdatePasswordRequest,  # Lấy mật khẩu mới từ request
#     token: str = Depends(security)  # Token xác thực
# ):
#     try:
#         # Lấy thông tin người dùng từ Supabase dựa trên token
#         user_info = supabase.auth.get_user(token.credentials)



#         # Cập nhật mật khẩu
#         update_response = supabase.auth.update_user(
#             user_info["id"], {"password": body.new_password}
#         )

#         if update_response.error:
#             raise HTTPException(status_code=400, detail=update_response.error.message)

#         return {"message": "Password updated successfully"}

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))




# @router.post("/logout", tags=["User"])
# def logout(request: Request, user=Depends(auth_guard)):
#     """
#     API để user logout, thu hồi refresh token của họ.
#     """
#     user_id = user.get("uid")
#     if not user_id:
#         raise HTTPException(status_code=401, detail="User not authenticated")

#     try:
#         # Gọi Supabase để logout
#         supabase.auth.sign_out()

#         return {"message": "User logged out successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error logging out: {str(e)}")

# @router.patch("/change-password", tags=["User"])
# def change_password(
#     request: Request,
#     payload: ChangePasswordSchema,
#     user_service: UserService = Depends(),
#     user=Depends(auth_guard)
# ):
#     user_id = user.get("uid")
#     if not user_id:
#         raise HTTPException(status_code=401, detail="User not authenticated")
    
#     return user_service.change_password(user_id, payload)

# @router.delete("/delete-account", tags=["User"])
# def delete_account(request: Request, user_service: UserService = Depends(), user=Depends(auth_guard)):
#     """
#     API xóa tài khoản người dùng sau khi đã xác thực.
#     """
#     user_id = user.get("uid")

#     if not user_id:
#         raise HTTPException(status_code=401, detail="User not authenticated")

#     try:
#         user_service.delete_user(user_id)  # ✅ Gọi hàm trong service để xử lý
#         return {"message": f"User {user_id} đã bị xóa thành công."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Không thể xóa người dùng: {str(e)}")
    

# @router.post("/{user_id}", response_model=dict)
# def create_user(user_id: str, user_data: UserCreate):
#     return UserService.create_user(user_id, user_data)

# @router.put("/{user_id}", response_model=dict)
# def update_user(user_id: str, update_data: UserUpdate):
#     return UserService.update_user(user_id, update_data)

# @router.get("/{user_id}", response_model=dict)
# def get_user(user_id: str):
#     user = UserService.get_user(user_id)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user
