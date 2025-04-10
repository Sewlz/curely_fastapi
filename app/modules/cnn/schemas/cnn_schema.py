from pydantic import BaseModel
from typing import List, Optional

class PredictionResult(BaseModel):
    message: str
    prediction: str
    confidence: float

class DiagnosisRecord(BaseModel):
    diagnosisId: str
    historyId: str
    mriImageUrl: str
    aiPrediction: str
    confidenceScore: float
    diagnosedAt: Optional[str] = None