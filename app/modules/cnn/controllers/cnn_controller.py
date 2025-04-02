from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.modules.cnn.services.cnn_service import predict_image

router = APIRouter()

@router.post("/predict")
async def predict(image: UploadFile = File(...)):
    return await predict_image(image)
