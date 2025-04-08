from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class InputData(BaseModel):
    session_id: str
    prompt: str

class OutputData(BaseModel):
    response: str

class ChatMessageSchema(BaseModel):
    session_id: str
    user_id: str
    sender: str
    message: str
    timestamp: Optional[datetime] = None

class ChatSessionCreate(BaseModel):
    session_name: str
    
class ChatSession(BaseModel):
    session_id: str
    user_id: str
    session_name: str
    status: str
    created_at: Optional[datetime]
