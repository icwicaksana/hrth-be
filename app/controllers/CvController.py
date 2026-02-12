from fastapi import UploadFile, HTTPException
from app.services.CvAnalyzerService import CvAnalyzerService
from app.tools.file_handler import FileHandler
from app.llm.factory import get_llm
import uuid

class CvController:
    async def analyze(self, file: UploadFile, job_position_id: int, user_id: str):
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        try:
            file_bytes = await file.read()
            file_path = f"cvs/{uuid.uuid4()}.pdf"
            
            # Upload to Storage
            await FileHandler.upload_file(file_bytes, file_path)
            
            # Init Service with LLM
            llm = get_llm()
            service = CvAnalyzerService(llm=llm)
            
            # Process
            # User ID is now passed from the route
            result = await service(user_id, job_position_id, file_path, file_bytes)
            
            return {"status": "success", "data": result}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
