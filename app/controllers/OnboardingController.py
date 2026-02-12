from fastapi import UploadFile, HTTPException
from typing import List, Dict, Any
from app.services.OnboardingService import OnboardingService
from app.tools.file_handler import FileHandler
from app.llm.factory import get_llm
import uuid

class OnboardingController:
    async def analyze(
        self,
        file_ktp: UploadFile,
        file_cv: UploadFile,
        job_position_id: int,
        join_date: str,
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

            await process_file(file_ktp, "ktp", "onboarding/ktp")
            await process_file(file_cv, "cv", "onboarding/cv")
            
            llm = get_llm()
            service = OnboardingService(llm=llm)
            
            # Analyze only
            result = await service.analyze(user_id, job_position_id, join_date, processed_files)
            return {"status": "success", "data": result}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def generate_doc(self, data: Dict[str, Any], user_id: str):
        try:
            llm = get_llm()
            service = OnboardingService(llm=llm)
            
            # Generate doc only
            url = await service.generate_document(user_id, data)
            return {"status": "success", "document_url": url}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
