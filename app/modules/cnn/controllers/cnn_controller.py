from typing import List
from app.common.security.auth import auth_guard
from app.modules.cnn.services.cnn_service import CNNService
from app.modules.cnn.schemas.cnn_schema import PredictionResult
from app.common.validators.prediction_type import PredictType
from app.common.validators.validate_image import validate_image_file
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query 

router = APIRouter()
cnn_service = CNNService()

@router.post("/predict/{predict_type}", response_model=PredictionResult)
async def predict(predict_type:PredictType, image: UploadFile = File(...),  user = Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        validate_image_file(image)
        predict_type = predict_type.value
        return await cnn_service.predict_image(image, predict_type, user_id)
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
    
@router.delete("/history-multi")
def delelte_multiHistory(uuid_list: list[str] , user=Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        print(f'controller: list history {uuid_list}')
        return cnn_service.delete_user_multiHistory(user_id, uuid_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error when deleting multi history: {str(e)}")

