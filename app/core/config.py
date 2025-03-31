from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
    AES_SECRET_KEY = os.getenv("AES_SECRET_KEY")
    AES_IV = os.getenv("AES_IV")

settings = Settings()
