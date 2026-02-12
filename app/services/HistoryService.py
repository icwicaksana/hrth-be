from config.supabase import supabase_client
from app.tools.file_handler import FileHandler

class HistoryService:
    
    @staticmethod
    async def get_logs(limit: int = 50, offset: int = 0):
        # Supabase join syntax: select("*, profiles(*)")
        res = supabase_client.table("activity_logs").select("*, profiles(full_name, email)").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        return res.data

    @staticmethod
    async def delete_log(log_id: str):
        # 1. Fetch log to get file paths
        res = supabase_client.table("activity_logs").select("input_files, output_files").eq("id", log_id).single().execute()
        if not res.data:
            raise ValueError("Log not found")
            
        input_files = res.data.get("input_files") or []
        output_files = res.data.get("output_files") or []
        
        # 2. Delete files
        all_files = input_files + output_files
        for path in all_files:
            if path:
                try:
                    await FileHandler.delete_file(path)
                except Exception:
                    pass # Ignore if file missing
                    
        # 3. Delete Record
        supabase_client.table("activity_logs").delete().eq("id", log_id).execute()

