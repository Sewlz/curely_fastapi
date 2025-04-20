from pydantic import BaseModel

class SecureBaseModel(BaseModel):
    class Config:
        anystr_strip_whitespace = True
        min_anystr_length = 1
        max_anystr_length = 1000
