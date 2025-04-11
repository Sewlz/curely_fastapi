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
        timestamp = datetime.utcnow().isoformat()

        try:
            result = supabase.table("diagnosisHistory").select("historyId").eq("userId", user_id).limit(1).execute()

            if result.data:
                # If the user has history
                history_id = result.data[0]['historyId']
            else:
                # If user has no history then create new history
                history_id = str(uuid.uuid4())
                supabase.table("diagnosisHistory").insert({
                    "historyId": history_id,
                    "userId": user_id,
                    "updatedAt": timestamp
                }).execute()

            # save data to table 'diagnoses'
            record = DiagnosisRecord(
                diagnosisId=diagnosis_id,
                historyId=history_id,
                mriImageUrl=image_url,
                aiPrediction=prediction,
                confidenceScore=confidence,
                diagnosedAt=timestamp
            )

            supabase.table("diagnoses").insert(record.dict()).execute()

        except APIError as e:
            print("Supabase API Error:", e)
            raise

        return diagnosis_id

    @staticmethod
    def get_user_history(user_id: str):
        try:
            user_uuid = str(UUID(user_id))

            hitory_result = supabase.table('diagnosisHistory').select('historyId').eq("userId", user_uuid).execute()
            if not hitory_result.data:
                return []
            
            historyId = [entry['historyId'] for entry in hitory_result.data]
            result = supabase.table("diagnoses") \
                .select("*") \
                .in_("historyId", historyId) \
                .order("diagnosedAt", desc=True) \
                .execute()
            
            history = result.data

            for item in history:
                raw_url = item.get("mriImageUrl")
                signed_url = None

                if raw_url and "/storage/v1/object/public/imagebucket/" in raw_url:
                    try:
                        clean_url = raw_url.split('?')[0]
                        file_path_inside_bucket = clean_url.split("/storage/v1/object/public/imagebucket/")[-1]
                        bucket_name = "imagebucket"

                        print(f"Bucket: {bucket_name}, Path inside: {file_path_inside_bucket}")

                        # Lấy public URL nếu bucket đang ở chế độ public
                        signed_response = supabase.storage \
                            .from_(bucket_name) \
                            .get_public_url(file_path_inside_bucket)

                        signed_url = signed_response if signed_response else None

                    except Exception as sign_err:
                        print(f"[ERROR] Lỗi tạo signed URL: {sign_err}")

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


    @staticmethod
    def delete_history_record(user_id: str, diagnosis_id: str):
        # check diagnosis_id have exsist in user
        result = supabase.table('diagnoses').select("diagnosisId, historyId").eq("diagnosisId", diagnosis_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi")
        
        diagnosis = result.data[0]
        history_id = diagnosis["historyId"]

        history_result = supabase.table("diagnosisHistory").select("userId").eq("historyId", history_id).execute()
        if not history_result.data or history_result.data[0]["userId"] != user_id:
            raise HTTPException(status_code=403, detail="Bạn không có quyền xóa bản ghi này")

        # delete data in table diagnoses
        diagnosis_result = supabase.table('diagnoses').delete().eq("diagnosisId", diagnosis_id).execute()

        if not diagnosis_result.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi trong diagnoses")

        return {"message": "Delete Successful!"}


