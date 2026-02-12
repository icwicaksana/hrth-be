from fastapi import UploadFile, HTTPException
from typing import List, Dict, Any
from app.services.BgCheckService import BgCheckService
from app.tools.file_handler import FileHandler
from app.llm.factory import get_llm
import uuid

class BgCheckController:
    async def analyze(
        self,
        file_ktp: UploadFile,
        file_ijazah: UploadFile,
        file_skck: UploadFile,
        job_position_id: int,
        interview_passed: bool,
        reference_checked: bool,
        user_id: str
    ):
        try:
            processed_files = {}
            
            # Helper to upload
            async def process_file(file, key, folder):
                bytes_ = await file.read()
                path = f"{folder}/{uuid.uuid4()}_{file.filename}"
                await FileHandler.upload_file(bytes_, path, file.content_type)
                processed_files[key] = {
                    "name": file.filename,
                    "bytes": bytes_,
                    "path": path,
                    "mime_type": file.content_type
                }

            await process_file(file_ktp, "ktp", "bg_check/ktp")
            await process_file(file_ijazah, "academic", "bg_check/academic")
            await process_file(file_skck, "criminal", "bg_check/criminal")
            
            manual_data = {
                "job_position_id": job_position_id,
                "interview_passed": interview_passed,
                "reference_checked": reference_checked,
            }
            
            llm = get_llm()
            service = BgCheckService(llm=llm)
            
            # Analyze only
            result = await service.analyze(user_id, manual_data, processed_files)
            return {"status": "success", "data": result}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def generate_doc(self, data: Dict[str, Any], user_id: str):
        try:
            llm = get_llm()
            service = BgCheckService(llm=llm)
            
            # Generate doc only
            url = await service.generate_document(user_id, data)
            return {"status": "success", "document_url": url}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
