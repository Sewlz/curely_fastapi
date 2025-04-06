# import firebase_admin
# from firebase_admin import credentials, firestore
# from app.core.config import settings

# # Khởi tạo Firestore
# cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
# firebase_admin.initialize_app(cred)
# db = firestore.client()


import os
from supabase import create_client, Client
import dotenv

dotenv.load_dotenv()


def supabase_db():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_ANON_KEY")
    supabase_client: Client = create_client(url, key)
    return supabase_client