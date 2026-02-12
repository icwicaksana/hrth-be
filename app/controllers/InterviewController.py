from fastapi import HTTPException
from typing import Dict, Any
from app.services.InterviewService import InterviewService
from app.llm.factory import get_llm
from app.schemas.HrSchemas import InterviewAnalysisRequest
import logging

logger = logging.getLogger(__name__)

class InterviewController:
    async def analyze(
        self,
        request: InterviewAnalysisRequest,
        user_id: str
    ):
        try:
            llm = get_llm()
            service = InterviewService(llm=llm)
            
            result = await service(user_id, request.file_path)
            return {"status": "success", "data": result}
            
        except Exception as e:
            logger.error(f"Interview Analysis Failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
