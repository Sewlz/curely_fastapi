import smtplib
import os
import firebase_admin
from firebase_admin import auth
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
import requests
from app.modules.auth.schemas.auth_schema import RegisterUserSchema, LoginSchema
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
API_KEY = os.getenv("APIKEY")

class AuthService:
    # REGISTER
    @staticmethod
    def register_user( user_data: RegisterUserSchema):
        try:
            # ✅ Chuẩn hóa số điện thoại
            phone_number = user_data.phone_number.strip()
            if phone_number.startswith("0"):
                phone_number = "+84" + phone_number[1:]
            elif not phone_number.startswith("+"):
                phone_number = "+84" + phone_number
            # ✅ Tạo user trên Firebase
            user = auth.create_user(
                email=user_data.email,
                password=user_data.password,
                display_name=f"{user_data.first_name} {user_data.last_name}",
                phone_number=phone_number or ""
            )
             # ✅ Gán quyền mặc định là "user"
            auth.set_custom_user_claims(user.uid, {"role": "user"})

            # 🔥 Tạo link xác minh email
            verification_link = auth.generate_email_verification_link(user.email)

            # ✅ Gửi email chứa link xác minh ngay tại đây
            subject = "Verify Your Account"
            body = f"""
            <html>
            <body>
                <h2>Hello,</h2>
                <p>Thank you for registering. Please verify your email by clicking the link below:</p>
                <a href="{verification_link}">{verification_link}</a>
                <p>If you did not request this, please ignore this email.</p>
            </body>
            </html>
            """
            msg = MIMEMultipart()
            msg["From"] = SMTP_EMAIL
            msg["To"] = user_data.email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            # ✅ Gửi email qua SMTP
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, user_data.email, msg.as_string())
            server.quit()

            return {
                "message": "User registered successfully. Please check your email to verify your account.",
                "uid": user.uid,
                "email": user.email,
                "role": "user"
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # lOGIN 
    @staticmethod
    def login_user(user_data: LoginSchema):
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
            
            payload = {
                "email": user_data.email,
                "password": user_data.password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Tài khoản hoặc mật khẩu không đúng!")

            data = response.json()
            id_token = data["idToken"]
            refresh_token = data["refreshToken"]

            # ✅ Lấy thông tin user từ Firebase
            decoded_token = auth.verify_id_token(id_token)
            user = auth.get_user(decoded_token["uid"])

            # 🔥 Kiểm tra email đã xác minh chưa
            if not user.email_verified:
                raise HTTPException(status_code=403, detail="Email chưa được xác minh. Vui lòng kiểm tra email của bạn.")

            # ✅ Lấy role từ custom claims
            user_claims = user.custom_claims or {}
            role = user_claims.get("role", "user")

            return {
                "idToken": id_token,
                "refreshToken": refresh_token,
                "role": role,
                "expiresIn": data["expiresIn"]
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    



    # FORGOT PASSWORD
    @staticmethod
    def forgot_password( email: str):
        try:
            # ✅ Kiểm tra user có tồn tại không
            try:
                user = auth.get_user_by_email(email)
            except auth.UserNotFoundError:
                raise HTTPException(status_code=404, detail="Email không tồn tại trong hệ thống.")

            # 🔥 Tạo link đặt lại mật khẩu
            reset_link = auth.generate_password_reset_link(email)

            # ✅ Gửi email chứa link đặt lại mật khẩu qua SMTP
            subject = "Reset Your Password"
            body = f"""
            <html>
            <body>
                <h2>Reset Your Password</h2>
                <p>Click the link below to reset your password:</p>
                <a href="{reset_link}">{reset_link}</a>
                <p>If you did not request this, please ignore this email.</p>
            </body>
            </html>
            """
            msg = MIMEMultipart()
            msg["From"] = SMTP_EMAIL
            msg["To"] = email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            # ✅ Gửi email
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, email, msg.as_string())
            server.quit()

            return {"message": "Email đặt lại mật khẩu đã được gửi!"}

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))




    # LOGIN GOOGLE
    @staticmethod
    def login_with_google(id_token: str):
        try:
            # ✅ Xác minh ID token từ Google
            decoded_token = auth.verify_id_token(id_token)
            if not decoded_token:
                raise HTTPException(status_code=400, detail="Invalid Google Token")

            # ✅ Trích xuất thông tin user từ token đã giải mã
            uid = decoded_token.get("uid")
            email = decoded_token.get("email")
            display_name = decoded_token.get("name", "")
            photo_url = decoded_token.get("picture", "")
            email_verified = decoded_token.get("email_verified", False)

            # ✅ Kiểm tra user có tồn tại trên Firebase chưa
            try:
                user_record = auth.get_user(uid)
                role = user_record.custom_claims.get("role", "user") if user_record.custom_claims else "user"
            except auth.UserNotFoundError:
                # 🔥 Nếu user chưa có, tạo mới tài khoản
                user_record = auth.create_user(
                    uid=uid,
                    email=email,
                    display_name=display_name,
                    photo_url=photo_url,
                    email_verified=email_verified
                )
                role = "user"
                auth.set_custom_user_claims(user_record.uid, {"role": role})

            # ✅ Tạo Custom Token cho Firebase Authentication
            custom_token = auth.create_custom_token(uid).decode("utf-8")

            return {
                "message": "Google login successful",
                "uid": uid,
                "email": email,
                "displayName": display_name,
                "photoURL": photo_url,
                "role": role,
                "access_token": custom_token,
                "email_verified": email_verified
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Google login failed: {str(e)}")





    # lOGIN FACEBOOK 
    @staticmethod  
    def login_with_facebook(id_token: str):
        try:
            # ✅ Xác minh ID token từ Facebook với Firebase
            decoded_token = auth.verify_id_token(id_token)
            if not decoded_token:
                raise HTTPException(status_code=400, detail="Invalid Facebook Token")

            # ✅ Trích xuất thông tin user từ token đã giải mã
            uid = decoded_token.get("uid")
            email = decoded_token.get("email")
            display_name = decoded_token.get("name", "")
            photo_url = decoded_token.get("picture", "")

            # ✅ Kiểm tra user có tồn tại trên Firebase chưa
            try:
                user_record = auth.get_user(uid)
                role = user_record.custom_claims.get("role", "user") if user_record.custom_claims else "user"
            except auth.UserNotFoundError:
                # 🔥 Nếu user chưa có, tạo mới tài khoản
                user_record = auth.create_user(
                    uid=uid,
                    email=email,
                    display_name=display_name,
                    photo_url=photo_url,
                )
                role = "user"
                auth.set_custom_user_claims(user_record.uid, {"role": role})

            # ✅ Tạo Custom Token cho Firebase Authentication
            custom_token = auth.create_custom_token(uid).decode("utf-8")

            return {
                "message": "Facebook login successful",
                "uid": uid,
                "email": email,
                "displayName": display_name,
                "photoURL": photo_url,
                "role": role,
                "access_token": custom_token
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Facebook login failed: {str(e)}")
