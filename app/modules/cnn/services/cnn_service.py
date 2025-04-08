import tempfile
from fastapi import UploadFile, HTTPException
from supabase import SupabaseException
from app.modules.cnn.schemas.cnn_schema import PredictionResult
from PIL import Image
import numpy as np
import tensorflow as tf
from uuid import uuid4
from datetime import timedelta
import os
from app.common.database.supabase import supabase
from app.modules.cnn.repositories.cnn_repository import CNNRepository
from app.modules.cnn.config.cnn_config import MODEL_PATH, CLASS_LABELS

model = tf.keras.models.load_model(MODEL_PATH)
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
    def get_prediction_history(user_id: str):
        try:
            return CNNRepository.get_user_history(user_id)
        except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")        

    async def predict_image(self, image: UploadFile, user_id: str):
        try:
            file_id = f"{uuid4()}.png"

            # Predict
            image.file.seek(0)
            image_data = Image.open(image.file)
            processed_image = self.preprocess_image(image_data)
            predictions = model.predict(processed_image)
            predicted_index = np.argmax(predictions)
            predicted_class = CLASS_LABELS[predicted_index]
            confidence = float(predictions[0][predicted_index])

            # Save file temporarily
            image.file.seek(0)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(image.file.read())
                tmp_path = tmp.name

            # Upload to Supabase
            try:
                supabase.storage.from_("imagebucket").upload(file_id, tmp_path)
            except SupabaseException as e:
                raise HTTPException(status_code=500, detail=f"Supabase upload failed: {str(e)}")

            os.remove(tmp_path)

            public_url = supabase.storage.from_("imagebucket").get_public_url(file_id)

            CNNRepository.save_diagnosis(user_id, public_url, predicted_class, confidence)

            return PredictionResult(
                message="Prediction successful",
                prediction=predicted_class,
                confidence=confidence
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
        
    @staticmethod
    def delete_user_history(user_id: str, diagnosis_id: str):
        try:
            return CNNRepository.delete_history_record(user_id, diagnosis_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting history record: {str(e)}")




