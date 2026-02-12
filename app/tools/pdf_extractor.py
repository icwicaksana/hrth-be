import io
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)

class PdfExtractor:
    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes) -> str:
        """
        Extracts text from PDF bytes.
        """
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"PDF Extraction error: {str(e)}")
            raise

