import uuid
from datetime import datetime, timedelta
from app.common.database.supabase import supabase
from app.modules.cnn.schemas.cnn_schema import DiagnosisRecord
from concurrent.futures import ThreadPoolExecutor, as_completed
from postgrest.exceptions import APIError
import time
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
            history_result = supabase.table('diagnosisHistory').select('historyId').eq("userId", user_uuid).execute()

            if not history_result.data:
                return []

            history_ids = [entry['historyId'] for entry in history_result.data]
            result = supabase.table("diagnoses") \
                .select("*") \
                .in_("historyId", history_ids) \
                .order("diagnosedAt", desc=True) \
                .execute()

            history = result.data

            # Get file list once
            folder_path = "mri"
            file_objs = supabase.storage.from_("imagebucket").list(folder_path)
            file_list = set(f["name"] for f in file_objs)

            # Generate signed URLs concurrently
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_map = {
                    executor.submit(CNNRepository.get_signed_image_url, item["mriImageUrl"], file_list): item
                    for item in history
                }

                for future in as_completed(future_map):
                    item = future_map[future]
                    try:
                        signed_url = future.result()
                    except Exception as e:
                        print(f"[ERROR] Signed URL future failed: {e}")
                        signed_url = None

                    item["signedImageUrl"] = signed_url

            return history

        except Exception as e:
            print(f"[ERROR] Retrieving history with signed image URLs: {e}")
            return []
    
    @staticmethod
    def get_signed_image_url(image_url: str, file_list: set, retries: int = 2) -> str | None:
        try:
            image_url = image_url.split("?")[0]
            filename = image_url.split("/")[-1]
            folder_path = "mri"
            file_path = f"{folder_path}/{filename}"

            if filename not in file_list:
                print(f"[SKIP] File '{filename}' not found in folder '{folder_path}'")
                return None

            for attempt in range(retries):
                try:
                    signed_response = supabase.storage \
                        .from_("imagebucket") \
                        .create_signed_url(file_path, int(timedelta(minutes=180).total_seconds()))
                    
                    return signed_response.get("signedURL") if signed_response else None
                except Exception as e:
                    print(f"[RETRY {attempt+1}] Signed URL error: {e}")
                    time.sleep(0.5)

            return None

        except Exception as e:
            print(f"[ERROR] Generating signed image URL: {e}")
            return None

    @staticmethod
    def delete_history_record(user_id: str, diagnosis_id: str):
        # check diagnosis_id have exsist in user
        result = supabase.table('diagnoses').select("diagnosisId, historyId").eq("diagnosisId", diagnosis_id)
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

