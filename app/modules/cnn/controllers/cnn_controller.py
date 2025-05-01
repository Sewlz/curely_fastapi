from typing import List
from fastapi.responses import JSONResponse
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
        result = await cnn_service.predict_image(image, predict_type, user_id)
        return JSONResponse(status_code=200, content={"success": True,"data": result,"message": "Predicting image successfully."})
    except HTTPException as http_ex:
        return JSONResponse(
            status_code=http_ex.status_code,
            content={
                "success": False,
                "error": {
                    "code": http_ex.status_code,
                    "message": f"Error predicting image:{http_ex.detail}"
                }
            }
        )
@router.get("/history", response_model=List[dict])
def get_history(user = Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        result = cnn_service.get_prediction_history(user_id)
        return JSONResponse(status_code=200, content={"success": True,"data": result,"message": "Fetching history successfully."})
    except HTTPException as http_ex:
        return JSONResponse(
            status_code=http_ex.status_code,
            content={
                "success": False,
                "error": {
                    "code": http_ex.status_code,
                    "message": f"Error fetching history:{http_ex.detail}"
                }
            }
        )    
@router.delete("/history/{diagnosis_id}")
def delete_history(diagnosis_id: str, user=Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        result = cnn_service.delete_user_history(user_id, diagnosis_id)
        return JSONResponse(status_code=200, content={"success": True,"data": result,"message": "Delete history successfully."})
    except HTTPException as http_ex:
        return JSONResponse(
            status_code=http_ex.status_code,
            content={
                "success": False,
                "error": {
                    "code": http_ex.status_code,
                    "message": f"Error Deleting history:{http_ex.detail}"
                }
            }
        )      
@router.delete("/history-multi")
def delelte_multiHistory(uuid_list: list[str] , user=Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        result = cnn_service.delete_user_multiHistory(user_id, uuid_list)
        print(f'controller: list history {uuid_list}')
        return  JSONResponse(status_code=200, content={"success": True,"data": result,"message": "History deleted successfully."})
    except HTTPException as http_ex:
        return JSONResponse(
            status_code=http_ex.status_code,
            content={
                "success": False,
                "error": {
                    "code": http_ex.status_code,
                    "message": f"Error when deleting multiple history: {http_ex.detail}"
                }
            }
        )