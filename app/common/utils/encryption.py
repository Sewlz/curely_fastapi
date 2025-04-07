# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad, unpad
# import base64
# import os
# import hashlib

# def fix_aes_key(key: str, length: int = 32) -> bytes:
#     """
#     Chuyển đổi key về độ dài hợp lệ (16, 24, 32 byte) bằng SHA-256.
#     """
#     return hashlib.sha256(key.encode()).digest()[:length]

# SECRET_KEY = fix_aes_key(os.getenv("AES_SECRET_KEY", "default_secret_key"), 32)
# IV = fix_aes_key(os.getenv("AES_IV", "default_iv"), 16)  # IV phải có 16 byte

# class AESCipher:
#     def __init__(self, key: bytes, iv: bytes):
#         self.key = key
#         self.iv = iv

#     def encrypt(self, data: str) -> str:
#         cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
#         padded_data = pad(data.encode(), AES.block_size)  # Sử dụng padding PKCS7
#         encrypted = cipher.encrypt(padded_data)
#         return base64.b64encode(encrypted).decode()

#     def decrypt(self, data: str) -> str:
#         cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
#         decrypted = cipher.decrypt(base64.b64decode(data))
#         return unpad(decrypted, AES.block_size).decode()

# aes_cipher = AESCipher(SECRET_KEY, IV)