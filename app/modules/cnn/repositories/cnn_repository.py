import os
import time
import uuid
import tempfile
from uuid import UUID
from uuid import uuid4
from supabase import SupabaseException
from datetime import datetime, timedelta
from postgrest.exceptions import APIError
from fastapi import UploadFile, HTTPException
from app.common.database.supabase import supabase
from app.modules.cnn.schemas.cnn_schema import DiagnosisRecord
from concurrent.futures import ThreadPoolExecutor, as_completed

class CNNRepository:
    @staticmethod
    async def save_diagnosis(user_id: str, image_url: str, prediction: str, confidence: float, predict_type: str):
        try:
            diagnosis_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            typeId = await CNNRepository.get_type_id(predict_type)
            history_id = CNNRepository.get_or_create_history_id(user_id, timestamp)

            record = DiagnosisRecord(
                diagnosisId=diagnosis_id,
                typeId=typeId,
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
    def get_or_create_history_id(user_id: str, timestamp: str) -> str:
        result = supabase.table("diagnosisHistory").select("historyId").eq("userId", user_id).limit(1).execute()

        if result.data:
            return result.data[0]['historyId']

        history_id = str(uuid4())
        supabase.table("diagnosisHistory").insert({
            "historyId": history_id,
            "userId": user_id,
            "updatedAt": timestamp
        }).execute()

        return history_id

    @staticmethod
    async def get_type_id(type: str) -> str:
        try:
            result = supabase.table('diagnosisType').select("id").eq("name", type).limit(1).execute()
            if result.data:
                print("get_type_id:", result.data[0]['id'])
                return result.data[0]['id']
            else:
                raise ValueError(f"Diagnosis type '{type}' not found.")
        except APIError as e:
            print("Supabase API Error:", e)
            raise

    @staticmethod
    async def upload_image(image: UploadFile):
        try:
            file_id = f"{uuid4()}.png"
            # Save file temporarily
            image.file.seek(0)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(image.file.read())
                tmp_path = tmp.name

            # Upload to Supabase
            try:
                file_path = f"mri/{file_id}"
                supabase.storage.from_("imagebucket").upload(file_path, tmp_path)
            except SupabaseException as e:
                raise HTTPException(status_code=500, detail=f"Supabase upload failed: {str(e)}")

            os.remove(tmp_path)

            public_url = supabase.storage.from_("imagebucket").get_public_url(f"mri/{file_id}")
            return public_url

        except Exception as e:    
            raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
        
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
    
    @staticmethod
    def delete_multiHistory_record(user_id: str, uuid_list: list[str]):
        existing_diagnoses = supabase.table('diagnoses')\
            .select('diagnosisId, historyId')\
            .in_('diagnosisId', uuid_list)\
            .execute()

        if not existing_diagnoses.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy diagnosisId nào trong bảng diagnoses.")

        found_ids = [item['diagnosisId'] for item in existing_diagnoses.data]
        history_ids = list(set([item['historyId'] for item in existing_diagnoses.data]))

        permission_result = supabase.table("diagnosisHistory")\
            .select("historyId, userId")\
            .in_("historyId", history_ids)\
            .execute()

        history_user_map = {item["historyId"]: item["userId"] for item in permission_result.data}
        unauthorized_ids = []

        for record in existing_diagnoses.data:
            if history_user_map.get(record["historyId"]) != user_id:
                unauthorized_ids.append(record["diagnosisId"])

        if unauthorized_ids:
            raise HTTPException(
                status_code=403,
                detail=f"You do not have permission to delete the following diagnosisIds: {unauthorized_ids}"
            )

        not_found = list(set(uuid_list) - set(found_ids))
        if not_found:
            print(f"Các ID không tồn tại: {not_found}")

        multiDiagnosis_result = supabase.table('diagnoses')\
            .delete()\
            .in_('diagnosisId', found_ids)\
            .execute()

        if not multiDiagnosis_result.data:
            raise HTTPException(status_code=404, detail="Error when deleting diagnosisId in table diagnoses!")

        return {
            "message": "Successfully deleted existing diagnosisId.!",
            "deleted_ids": found_ids,
            "not_found_ids": not_found
        }