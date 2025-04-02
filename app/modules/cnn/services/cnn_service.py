import numpy as np
from PIL import Image
import tensorflow as tf
from fastapi import UploadFile
from uuid import uuid4
from fastapi import HTTPException

# Load the trained CNN model
MODEL_PATH = "app\model_hub\mri_cnn_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

# Define class labels based on your model's output
CLASS_LABELS = ["glioma", "meningioma", "notumor", "pituitary"]

def preprocess_image(image: Image.Image):
    try:
        image = image.convert("RGB") 
        image = image.resize((256, 256))  
        image = np.array(image) / 255.0  
        image = np.expand_dims(image, axis=0)
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image processing error: {str(e)}")

async def predict_image(image: UploadFile):
    image_data = Image.open(image.file)
    processed_image = preprocess_image(image_data)  

    # Model Prediction
    predictions = model.predict(processed_image)
    predicted_class = CLASS_LABELS[np.argmax(predictions)]

    return {"message": "Prediction successful", "prediction": predicted_class}
