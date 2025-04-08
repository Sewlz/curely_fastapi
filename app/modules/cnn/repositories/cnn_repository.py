import uuid
from datetime import datetime, timedelta
from app.common.database.supabase import supabase
from app.modules.cnn.schemas.cnn_schema import DiagnosisRecord
from postgrest.exceptions import APIError
from uuid import UUID

class CNNRepository:
    @staticmethod
    def save_diagnosis(user_id: str, image_url: str, prediction: str, confidence: float):
        diagnosis_id = str(uuid.uuid4())
        diagnosed_at = datetime.utcnow().isoformat()

        try:
            record = DiagnosisRecord(
                diagnosisId=diagnosis_id,
                userId=user_id,
                mriImageUrl=image_url,
                aiPrediction=prediction,
                confidenceScore=confidence,
                diagnosedAt=diagnosed_at
            )

            supabase.table("diagnoses").insert(record.dict()).execute()

            # supabase.table("diagnosisHistory").insert({
            #     "historyId": str(uuid.uuid4()),
            #     "diagnosisId": diagnosis_id,
            #     "updatedAt": diagnosed_at
            # }).execute()

        except APIError as e:
            print("Supabase API Error:", e)
            raise

        return diagnosis_id

    @staticmethod
    def get_user_history(user_id: str):
        try:
            user_uuid = str(UUID(user_id))
            result = supabase.table("diagnoses") \
                .select("*") \
                .eq("userId", user_uuid) \
                .order("diagnosedAt", desc=True) \
                .execute()
    
            history = result.data
    
            for item in history:
                raw_url = item.get("mriImageUrl")
                signed_url = None
    
                if raw_url and "/storage/v1/object/public/" in raw_url:
                    clean_url = raw_url.split('?')[0]
                    # Lấy full path bên trong bucket, ví dụ: "imagebucket/uploads/file.png"
                    file_path = clean_url.split("/storage/v1/object/public/")[-1]
    
                    # Tách tên bucket và đường dẫn file
                    parts = file_path.split("/", 1)
                    if len(parts) == 2:
                        bucket_name, file_path_inside_bucket = parts
                        signed_response = supabase.storage \
                            .from_(bucket_name) \
                            .create_signed_url(file_path_inside_bucket, int(timedelta(minutes=180).total_seconds()))
    
                        signed_url = signed_response.get("signedURL") if signed_response else None
    
                item["signedImageUrl"] = signed_url
    
            return history
    
        except Exception as e:
            print(f"Error retrieving history with signed image URLs: {e}")
            return []


    @staticmethod
    def get_signed_image_url(user_id: str) -> str | None:
        try:
            # 1. Get the latest diagnosis record for the user
            result = supabase.table("diagnoses") \
                .select("mriImageUrl") \
                .eq("userId", user_id) \
                .order("diagnosedAt", desc=True) \
                .limit(1) \
                .execute()

            if not result.data:
                return None

            # 2. Extract the file path from the public image URL
            image_url = result.data[0]["mriImageUrl"]
            file_path = image_url.split("/object/public/")[-1]
            if not file_path:
                raise ValueError("Could not parse file path from image URL")

            # 3. Generate signed URL (valid for 180 minutes)
            signed_response = supabase.storage \
                .from_("imagebucket") \
                .create_signed_url(file_path, int(timedelta(minutes=180).total_seconds()))

            return signed_response.get("signedURL") if signed_response else None

        except Exception as e:
            print(f"Error generating signed image URL: {e}")
            return None
