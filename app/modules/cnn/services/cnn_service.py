import os
import numpy as np
from PIL import Image
from uuid import uuid4
import tensorflow as tf
from fastapi import HTTPException, UploadFile
from datetime import timedelta
from app.modules.cnn.schemas.cnn_schema import PredictionResult
from app.modules.cnn.repositories.cnn_repository import CNNRepository
from app.modules.cnn.config.cnn_config import MODEL_PATH, LC_MODEL_PATH, CLASS_LABELS, LUNG_CANCER_CLASSES

model = tf.keras.models.load_model(MODEL_PATH)
lungmodel = tf.keras.models.load_model(LC_MODEL_PATH)

class CNNService:
    @staticmethod
    def preprocess_image(image: Image.Image):
        try:
            image = image.convert("RGB")
            image = image.resize((256, 256))
            image = np.array(image) / 255.0
            image = np.expand_dims(image, axis=0)
            return image
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Image processing error: {str(e)}")

    @staticmethod
    def preprocess_lung_image(image: Image.Image):
        try:
            image = image.convert("RGB")
            image = image.resize((224, 224))
            image = np.array(image) / 255.0
            image = np.expand_dims(image, axis=0)
            return image
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Image processing error: {str(e)}")

    @staticmethod
    def get_prediction_history(user_id: str):
        try:
            return CNNRepository.get_user_history(user_id)
        except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error creating history: {str(e)}")

    @staticmethod
    async def predict_image(image: UploadFile, predict_type: str, user_id: str):
        try:
            data = {}
            if(predict_type == "brain"):
                data = CNNService.cnn_brain_predict(image)
            elif(predict_type == "lung"):
                data = CNNService.cnn_lung_predict(image)
            predicted_class = data["predicted_class"]
            confidence = data["confidence"]

            if (not predicted_class or not confidence):
                raise HTTPException(status_code=400, detail="Invalid prediction result")
            else:
                public_url = await CNNRepository.upload_image(image)
                await CNNRepository.save_diagnosis(user_id, public_url, predicted_class, confidence, predict_type)

            return PredictionResult(
                message="Prediction successful",
                aiPrediction=predicted_class,
                confidenceScore=confidence,
                predictType=predict_type
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
        
    @staticmethod
    def cnn_brain_predict(image:UploadFile):
        image.file.seek(0)
        image_data = Image.open(image.file)
        processed_image = CNNService.preprocess_image(image_data)
        predictions = model.predict(processed_image)
        predicted_index = np.argmax(predictions)
        predicted_class = CLASS_LABELS[predicted_index]
        confidence = float(predictions[0][predicted_index])
        data = {"predicted_class": predicted_class, "confidence": confidence}
        return data
    
    @staticmethod
    def cnn_lung_predict(image:UploadFile):
        image.file.seek(0)
        image_data = Image.open(image.file)
        processed_image = CNNService.preprocess_lung_image(image_data)
        predictions = lungmodel.predict(processed_image)
        predicted_index = np.argmax(predictions)
        print(predicted_index)
        predicted_class = LUNG_CANCER_CLASSES[predicted_index]
        confidence = float(predictions[0][predicted_index])
        data = {"predicted_class": predicted_class, "confidence": confidence}
        return data

    @staticmethod
    def delete_user_history(user_id: str, diagnosis_id: str):
        try:
            return CNNRepository.delete_history_record(user_id, diagnosis_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting history record: {str(e)}")