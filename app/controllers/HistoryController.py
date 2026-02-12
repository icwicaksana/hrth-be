from fastapi import HTTPException
from app.services.HistoryService import HistoryService

class HistoryController:
    async def get_history(self, limit: int, offset: int):
        try:
            data = await HistoryService.get_logs(limit, offset)
            return {"status": "success", "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_history(self, log_id: str):
        try:
            await HistoryService.delete_log(log_id)
            return {"status": "success", "message": "Log and files deleted"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
