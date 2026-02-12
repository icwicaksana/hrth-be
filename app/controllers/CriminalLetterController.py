from fastapi import UploadFile, HTTPException
from typing import Dict, Any
from app.services.CriminalLetterService import CriminalLetterService
from app.tools.file_handler import FileHandler
from app.llm.factory import get_llm
import uuid

class CriminalLetterController:
    async def analyze(
        self,
        file_ktp: UploadFile,
        job_position_id: int,
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

            await process_file(file_ktp, "ktp", "criminal_letter/ktp")
            
            llm = get_llm()
            service = CriminalLetterService(llm=llm)
            
            # Analyze
            result = await service.analyze(user_id, job_position_id, processed_files)
            return {"status": "success", "data": result}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def generate_doc(self, data: Dict[str, Any], user_id: str):
        try:
            llm = get_llm()
            service = CriminalLetterService(llm=llm)
            
            # Generate doc
            url = await service.generate_document(user_id, data)
            return {"status": "success", "document_url": url}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

