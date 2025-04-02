from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CNNResponseSchema(BaseModel):
    user_id: str
    image_url: str
    prediction: str
    timestamp: Optional[datetime] = None
