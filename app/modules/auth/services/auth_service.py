from supabase import create_client
from fastapi import HTTPException, Request
from app.modules.auth.repositories.auth_repository import AuthRepository
from app.modules.auth.schemas.auth_schema import RegisterUserSchema, LoginSchema
import os
from dotenv import load_dotenv
from datetime import datetime

# Load biến môi trường từ file .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")  # Client API Key
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")


# Khởi tạo Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

class AuthService:
    @staticmethod
    def register_user(user_data: RegisterUserSchema):
        """ Đăng ký người dùng với Supabase Auth và lưu thông tin vào bảng users """

        if user_data.password != user_data.confirm_password:
            raise HTTPException(status_code=400, detail="Password and confirm password do not match")

        # Đăng ký trên Auth
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })

        if hasattr(response, "error") and response.error:
            raise HTTPException(status_code=400, detail=response.error.message)

        user = response.user
        if not user or not user.id or not user.email:
            raise HTTPException(status_code=400, detail="Failed to retrieve user information after registration")

        # Lưu vào bảng users bằng repository
        user_data_to_insert = {
            "userId": user.id,
            "name": user_data.name,
            "email": user.email,
            "created_at": datetime.utcnow().isoformat(),
            "profilePicture": None  # để trống, cập nhật sau
        }
        AuthRepository.insert_user_data(user_data_to_insert)

        return {
            "uid": user.id,
            "email": user.email,
        }

    @staticmethod
    def login_user(user_data: LoginSchema):
        """ Đăng nhập người dùng với Supabase và trả về access token và refresh token """
        
        # Thực hiện đăng nhập với Supabase (sử dụng sign_in_with_password thay cho sign_in)
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        # Kiểm tra lỗi từ Supabase
        if hasattr(response, "error") and response.error:  # Kiểm tra nếu có lỗi
            raise HTTPException(status_code=400, detail=response.error.message)
        
        # Kiểm tra nếu không có session hoặc access token
        if not response.session or not response.session.access_token or not response.session.refresh_token:
            raise HTTPException(status_code=400, detail="Failed to retrieve tokens after login")
        
        # Trả về thông tin người dùng và token
        user = response.user
        if not user or not user.id:
            raise HTTPException(status_code=400, detail="Failed to retrieve user information after login")


        return {
            "message": "User logged in successfully",
            "uid": user.id,  # Lấy id của người dùng
            "email": user.email,
            "role": "user",  # Thêm role vào đây
            "idToken": response.session.access_token,  # Access token
            "refreshToken": response.session.refresh_token  # Refresh token
        }
    
    
    @staticmethod
    def refresh_token(refresh_token: str):
        """ Làm mới token bằng Supabase """
        try:
            session = supabase.auth.refresh_session(refresh_token)

            if not session or not session.session:
                raise HTTPException(status_code=400, detail="Invalid refresh token")

            return {
                "idToken": session.session.access_token,  # Token mới
                "refreshToken": session.session.refresh_token,  # Refresh token mới
                "expiresIn": session.session.expires_in  # Thời gian hết hạn
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    

    @staticmethod
    def login_with_google(id_token: str):
        """ Xác thực người dùng qua Google ID token """
        
        try:
            # Gửi ID token lên Supabase để xác thực
            response = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "id_token": id_token
            })
            
            # Kiểm tra lỗi từ Supabase
            if hasattr(response, "error") and response.error:
                raise HTTPException(status_code=400, detail=response.error.message)
            
            # Nếu không có session hoặc access token, báo lỗi
            if not response.session or not response.session.access_token:
                raise HTTPException(status_code=400, detail="Failed to retrieve tokens after Google login")
            
            # Trả về thông tin người dùng và token
            user = response.user
            return {
                "message": "User logged in successfully",
                "uid": user.id,
                "email": user.email,
                "role": "user",
                "idToken": response.session.access_token,  # Access token
                "refreshToken": response.session.refresh_token  # Refresh token
            }
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    def forgot_password(email: str):
        try:
            response = supabase.auth.reset_password_email(email)
            if hasattr(response, "error") and response.error:
                raise HTTPException(status_code=400, detail=response.error.message)
            return {"message": "Password reset email sent successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # @staticmethod
    # def login_with_google(id_token: str):
    #     try:
    #         # Xác thực id_token với Google và lấy thông tin người dùng
    #         CLIENT_ID = "463830006871-ulb9vvglh76tj52uokmjofu79g63lnsj.apps.googleusercontent.com.apps.googleusercontent.com"  # Thay bằng Client ID của bạn
    #         id_info = id_token.verify_oauth2_token(id_token, Request(), CLIENT_ID)

    #         # Lấy thông tin người dùng từ Google
    #         google_user = {
    #             "uid": id_info["sub"],  # Lấy user ID từ Google
    #             "email": id_info["email"],  # Email người dùng
    #             "name": id_info.get("name"),  # Tên người dùng
    #             "avatar_url": id_info.get("picture"),  # Avatar người dùng
    #         }

    #         # Trả về thông tin người dùng sau khi đăng nhập thành công
    #         return google_user

    #     except ValueError as e:
    #         raise HTTPException(status_code=400, detail="Invalid token")

# import smtplib
# import os
# from firebase_admin import auth
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from fastapi import HTTPException
# import requests
# from app.modules.auth.schemas.auth_schema import RegisterUserSchema, LoginSchema
# from app.modules.auth.repositories.auth_repository import AuthRepository
# from dotenv import load_dotenv

# # Load biến môi trường từ file .env
# load_dotenv()

# SMTP_EMAIL = os.getenv("SMTP_EMAIL")
# SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
# API_KEY = os.getenv("APIKEY")

# class AuthService:
#     # REGISTER
#     @staticmethod
#     def register_user( user_data: RegisterUserSchema):
#         try:
#              # Kiểm tra xem password và confirm_password có khớp không
#             if user_data.password != user_data.confirm_password:
#                 raise HTTPException(status_code=400, detail="Passwords do not match")
            
#             # ✅ Tạo user trên Firebase
#             user = auth.create_user(
#                 email=user_data.email,
#                 password=user_data.password,
#                 display_name=user_data.name,
#             )
#              # ✅ Gán quyền mặc định là "user"
#             auth.set_custom_user_claims(user.uid, {"role": "user"})

#             # 🔥 Lưu thông tin người dùng vào Firestore (bao gồm mã hóa thông tin)
#             user_info = {
#                 "email": user_data.email,
#                 "name": user_data.name,
#                 "role": "user",
#                 "birthday": "",
#                 "image": "",
#             }

#             # Gọi repository để lưu thông tin người dùng
#             AuthRepository.create_user(user.uid, user_info)


#             # 🔥 Tạo link xác minh email
#             verification_link = auth.generate_email_verification_link(user.email)

#             # ✅ Gửi email chứa link xác minh ngay tại đây
#             subject = "Verify Your Account"
#             body = f"""
#             <html>
#             <body>
#                 <h2>Hello,</h2>
#                 <p>Thank you for registering. Please verify your email by clicking the link below:</p>
#                 <a href="{verification_link}">{verification_link}</a>
#                 <p>If you did not request this, please ignore this email.</p>
#             </body>
#             </html>
#             """
#             msg = MIMEMultipart()
#             msg["From"] = f"Curely Support <{SMTP_EMAIL}>"  # Thay đổi tên hiển thị
#             msg["To"] = user_data.email
#             msg["Subject"] = subject
#             msg.attach(MIMEText(body, "html"))

#             # ✅ Gửi email qua SMTP
#             server = smtplib.SMTP("smtp.gmail.com", 587)
#             server.starttls()
#             server.login(SMTP_EMAIL, SMTP_PASSWORD)
#             server.sendmail(SMTP_EMAIL, user_data.email, msg.as_string())
#             server.quit()

#             return {
#                 "message": "User registered successfully. Please check your email to verify your account.",
#                 "uid": user.uid,
#                 "email": user.email,
#                 "role": "user"
#             }

#         except Exception as e:
#             raise HTTPException(status_code=400, detail=str(e))
        

    # # lOGIN 
    # @staticmethod
    # def login_user(user_data: LoginSchema):
    #     try:
    #         url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
            
    #         payload = {
    #             "email": user_data.email,
    #             "password": user_data.password,
    #             "returnSecureToken": True
    #         }
            
    #         response = requests.post(url, json=payload)
    #         if response.status_code != 200:
    #             raise HTTPException(status_code=400, detail="Tài khoản hoặc mật khẩu không đúng!")

    #         data = response.json()
    #         id_token = data["idToken"]
    #         refresh_token = data["refreshToken"]

    #         # ✅ Lấy thông tin user từ Firebase
    #         decoded_token = auth.verify_id_token(id_token)
    #         user = auth.get_user(decoded_token["uid"])

    #         # 🔥 Kiểm tra email đã xác minh chưa
    #         if not user.email_verified:
    #             raise HTTPException(status_code=403, detail="Email chưa được xác minh. Vui lòng kiểm tra email của bạn.")

    #         # ✅ Lấy role từ custom claims
    #         user_claims = user.custom_claims or {}
    #         role = user_claims.get("role", "user")

    #         return {
    #             "idToken": id_token,
    #             "refreshToken": refresh_token,
    #             "role": role,
    #             "expiresIn": data["expiresIn"]
    #         }
    #     except Exception as e:
    #         raise HTTPException(status_code=400, detail=str(e))
    



    # # FORGOT PASSWORD
    # @staticmethod
    # def forgot_password( email: str):
    #     try:
    #         # ✅ Kiểm tra user có tồn tại không
    #         try:
    #             user = auth.get_user_by_email(email)
    #         except auth.UserNotFoundError:
    #             raise HTTPException(status_code=404, detail="Email không tồn tại trong hệ thống.")

    #         # 🔥 Tạo link đặt lại mật khẩu
    #         reset_link = auth.generate_password_reset_link(email)

    #         # ✅ Gửi email chứa link đặt lại mật khẩu qua SMTP
    #         subject = "Reset Your Password"
    #         body = f"""
    #         <html>
    #         <body>
    #             <h2>Reset Your Password</h2>
    #             <p>Click the link below to reset your password:</p>
    #             <a href="{reset_link}">{reset_link}</a>
    #             <p>If you did not request this, please ignore this email.</p>
    #         </body>
    #         </html>
    #         """
    #         msg = MIMEMultipart()
    #         msg["From"] = SMTP_EMAIL
    #         msg["To"] = email
    #         msg["Subject"] = subject
    #         msg.attach(MIMEText(body, "html"))

    #         # ✅ Gửi email
    #         server = smtplib.SMTP("smtp.gmail.com", 587)
    #         server.starttls()
    #         server.login(SMTP_EMAIL, SMTP_PASSWORD)
    #         server.sendmail(SMTP_EMAIL, email, msg.as_string())
    #         server.quit()

    #         return {"message": "Email đặt lại mật khẩu đã được gửi!"}

    #     except Exception as e:
    #         raise HTTPException(status_code=400, detail=str(e))




    # # LOGIN GOOGLE
    # @staticmethod
    # def login_with_google(id_token: str):
    #     try:
    #         # ✅ Xác minh ID token từ Google
    #         decoded_token = auth.verify_id_token(id_token)
    #         if not decoded_token:
    #             raise HTTPException(status_code=400, detail="Invalid Google Token")

    #         # ✅ Trích xuất thông tin user từ token đã giải mã
    #         uid = decoded_token.get("uid")
    #         email = decoded_token.get("email")
    #         display_name = decoded_token.get("name", "")
    #         photo_url = decoded_token.get("picture", "")
    #         email_verified = decoded_token.get("email_verified", False)

    #         # ✅ Kiểm tra user có tồn tại trên Firebase chưa
    #         try:
    #             user_record = auth.get_user(uid)
    #             role = user_record.custom_claims.get("role", "user") if user_record.custom_claims else "user"
    #         except auth.UserNotFoundError:
    #             # 🔥 Nếu user chưa có, tạo mới tài khoản
    #             user_record = auth.create_user(
    #                 uid=uid,
    #                 email=email,
    #                 display_name=display_name,
    #                 photo_url=photo_url,
    #                 email_verified=email_verified
    #             )
    #             role = "user"
    #             auth.set_custom_user_claims(user_record.uid, {"role": role})

    #         # 🔥 Lưu thông tin người dùng vào Firestore (bao gồm mã hóa thông tin)
    #         user_info = {
    #             "email": email,
    #             "firstName": display_name.split(" ")[0],
    #             "lastName": " ".join(display_name.split(" ")[1:]),
    #             "role": role,
    #             "image": photo_url,
    #         }

    #         # Lưu vào Firestore
    #         AuthRepository.create_user(uid, user_info)

    #         # ✅ Tạo Custom Token cho Firebase Authentication
    #         custom_token = auth.create_custom_token(uid).decode("utf-8")

    #         return {
    #             "message": "Google login successful",
    #             "uid": uid,
    #             "email": email,
    #             "displayName": display_name,
    #             "photoURL": photo_url,
    #             "role": role,
    #             "access_token": custom_token,
    #             "email_verified": email_verified
    #         }

    #     except Exception as e:
    #         raise HTTPException(status_code=400, detail=f"Google login failed: {str(e)}")





    # # lOGIN FACEBOOK 
    # @staticmethod  
    # def login_with_facebook(id_token: str):
    #     try:
    #         # ✅ Xác minh ID token từ Facebook với Firebase
    #         decoded_token = auth.verify_id_token(id_token)
    #         if not decoded_token:
    #             raise HTTPException(status_code=400, detail="Invalid Facebook Token")

    #         # ✅ Trích xuất thông tin user từ token đã giải mã
    #         uid = decoded_token.get("uid")
    #         email = decoded_token.get("email")
    #         display_name = decoded_token.get("name", "")
    #         photo_url = decoded_token.get("picture", "")

    #         # ✅ Kiểm tra user có tồn tại trên Firebase chưa
    #         try:
    #             user_record = auth.get_user(uid)
    #             role = user_record.custom_claims.get("role", "user") if user_record.custom_claims else "user"
    #         except auth.UserNotFoundError:
    #             # 🔥 Nếu user chưa có, tạo mới tài khoản
    #             user_record = auth.create_user(
    #                 uid=uid,
    #                 email=email,
    #                 display_name=display_name,
    #                 photo_url=photo_url,
    #             )
    #             role = "user"
    #             auth.set_custom_user_claims(user_record.uid, {"role": role})

    #          # 🔥 Lưu thông tin người dùng vào Firestore (bao gồm mã hóa thông tin)
    #         user_info = {
    #             "email": email,
    #             "firstName": display_name.split(" ")[0],
    #             "lastName": " ".join(display_name.split(" ")[1:]),
    #             "role": role,
    #             "image": photo_url,
    #         }

    #         # Lưu vào Firestore
    #         AuthRepository.create_user(uid, user_info)
            
    #         # ✅ Tạo Custom Token cho Firebase Authentication
    #         custom_token = auth.create_custom_token(uid).decode("utf-8")

    #         return {
    #             "message": "Facebook login successful",
    #             "uid": uid,
    #             "email": email,
    #             "displayName": display_name,
    #             "photoURL": photo_url,
    #             "role": role,
    #             "access_token": custom_token
    #         }

    #     except Exception as e:
    #         raise HTTPException(status_code=400, detail=f"Facebook login failed: {str(e)}")
