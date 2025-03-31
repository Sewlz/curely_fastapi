from dotenv import load_dotenv
import os
import base64
import json

load_dotenv()

class Settings:
    FIREBASE_CREDENTIALS_BASE64 = os.getenv("FIREBASE_CREDENTIALS_BASE64")
    AES_SECRET_KEY = os.getenv("AES_SECRET_KEY")
    AES_IV = os.getenv("AES_IV")

    @property
    def FIREBASE_CREDENTIALS(self):
        if self.FIREBASE_CREDENTIALS_BASE64:
            decoded_data = base64.b64decode(self.FIREBASE_CREDENTIALS_BASE64).decode("utf-8")
            return json.loads(decoded_data)
        return None

settings = Settings()
