import os
import aiohttp
import aiofiles
import mimetypes
from typing import Optional
from urllib.parse import urlparse
from config.setting import env

class UrlUploader:
    def __init__(self, temp_dir: str = "dir"):
        self.temp_dir = temp_dir

    async def download_media(self, url: str) -> Optional[str]:
        """Download media from BSP URL to temporary file"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        # Get file extension from content-type or URL
                        content_type = response.headers.get('content-type', '')
                        url_path = urlparse(url).path
                        
                        # Try to get extension from content-type first
                        extension = mimetypes.guess_extension(content_type) or ''
                        
                        # If no extension from content-type, try to get from URL
                        if not extension and '.' in url_path:
                            extension = os.path.splitext(url_path)[1]
                        
                        # Generate temp filename with extension
                        random_id = os.urandom(8).hex()
                        filename = os.path.join(self.temp_dir, f"temp_{random_id}{extension}")
                        
                        # Save file
                        async with aiofiles.open(filename, 'wb') as f:
                            await f.write(await response.read())
                        
                        return filename
                    else:
                        return None
        except Exception as e:
            return None

    async def upload_file(self, filepath: str) -> Optional[str]:
        """Upload file to Siloam server"""
        try:
            # Prepare multipart form data
            data = aiohttp.FormData()
            
            # Determine content type based on file extension
            filename = os.path.basename(filepath)
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            # Use aiofiles for async file operations
            async with aiofiles.open(filepath, 'rb') as f:
                file_data = await f.read()
                data.add_field('files[]', 
                            file_data,
                            filename=filename,
                            content_type=content_type)  # Add content_type here
                
            data.add_field('uploader', 'assets')

            async with aiohttp.ClientSession() as session:
                async with session.post(env.base_url_uploader, data=data) as response:
                    print(f"response: {await response.text()}")
                    if response.status == 200:
                        result = await response.json()
                        # Get first file URL from response
                        if result.get('data') and len(result['data']) > 0:
                            return result['data'][0]['uri']
                    
                    return None
                    
        except Exception as e:
            return None
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    async def process_media(self, url: str) -> Optional[str]:
        """Process media from BSP URL to Siloam URL"""
        try:
            if not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir)
                
            # Download media
            temp_file = await UrlUploader.download_media(url)
            if not temp_file:
                return None

            # Upload to Siloam
            return await UrlUploader.upload_file(temp_file)

        except Exception as e:
            return None
