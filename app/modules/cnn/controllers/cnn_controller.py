from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from app.modules.cnn.services.cnn_service import CNNService
from app.modules.cnn.schemas.cnn_schema import PredictionResult
from typing import List
from app.common.security.auth import auth_guard 
router = APIRouter()
cnn_service = CNNService()

@router.post("/predict", response_model=PredictionResult)
async def predict(image: UploadFile = File(...),  user = Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        return await cnn_service.predict_image(image, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting image: {str(e)}")

@router.get("/history", response_model=List[dict])
def get_history(user = Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        return cnn_service.get_prediction_history(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")
    
@router.delete("/history/{diagnosis_id}")
def delete_history(diagnosis_id: str, user=Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        return cnn_service.delete_user_history(user_id, diagnosis_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting history: {str(e)}")

