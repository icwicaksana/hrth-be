import logging
from config.supabase import supabase_client
import os

logger = logging.getLogger(__name__)

class FileHandler:
    BUCKET_NAME = "hr-files"

    @staticmethod
    async def upload_file(file_bytes: bytes, destination_path: str, content_type: str = "application/pdf") -> str:
        """
        Uploads a file to Supabase Storage and returns the public URL or path.
        """
        try:
            res = supabase_client.storage.from_(FileHandler.BUCKET_NAME).upload(
                path=destination_path,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "false"}
            )
            # if res.error: # Supabase-py raises exc on error usually, but check just in case
            #     raise Exception(res.error.message)
            return destination_path
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            raise

    @staticmethod
    async def download_file(source_path: str) -> bytes:
        """
        Downloads a file from Supabase Storage.
        """
        try:
            res = supabase_client.storage.from_(FileHandler.BUCKET_NAME).download(source_path)
            return res
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            raise

    @staticmethod
    async def delete_file(path: str):
        """
        Deletes a file from Supabase Storage.
        """
        try:
            supabase_client.storage.from_(FileHandler.BUCKET_NAME).remove([path])
        except Exception as e:
            logger.error(f"Delete failed: {str(e)}")
            raise
            
    @staticmethod
    def get_public_url(path: str) -> str:
        return supabase_client.storage.from_(FileHandler.BUCKET_NAME).get_public_url(path)

