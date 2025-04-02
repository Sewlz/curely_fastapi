from pydantic import BaseModel

class InputData(BaseModel):
    prompt: str

class OutputData(BaseModel):
    response: str
