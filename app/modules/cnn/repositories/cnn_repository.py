import uuid
from datetime import datetime, timedelta
from app.common.database.supabase import supabase
from app.modules.cnn.schemas.cnn_schema import DiagnosisRecord
from postgrest.exceptions import APIError
from uuid import UUID
from fastapi import HTTPException


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
                try:
                    signed_url = CNNRepository.get_signed_image_url(user_id)
                except Exception as sign_err:
                    print(f"[ERROR] Lỗi tạo signed URL: {sign_err}")
                    signed_url = None

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
            file_path = image_url.split("/object/public/imagebucket")[-1]
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


    @staticmethod
    def delete_history_record(self, diagnosis_id: str):
        # 1. Xoá bảng diagnosisHistory trước
        history_result = supabase.table("diagnosis") \
            .delete() \
            .eq("diagnosisId", diagnosis_id) \
            .execute()

        # Kiểm tra có xóa được gì không
        if not history_result.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi trong diagnosisHistory")

        # 2. Xoá bảng diagnoses
        diagnosis_result = supabase.table("diagnoses") \
            .delete() \
            .eq("diagnosisId", diagnosis_id) \
            .execute()

        if not diagnosis_result.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi trong diagnoses")

        return {"message": "Delete Successful!"}


