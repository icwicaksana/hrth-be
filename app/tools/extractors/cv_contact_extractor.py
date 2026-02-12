import base64
from typing import Dict, Any
from core.BaseAgent import BaseAgent
from pydantic import BaseModel, Field

class CvContactOutput(BaseModel):
    email: str = Field(..., description="Email address extracted from the CV.")
    phone: str = Field(..., description="Phone number extracted from the CV.")

class CvContactExtractor(BaseAgent):
    def __init__(self, llm, **kwargs):
        prompt_template = """
        You are a Document Data Extractor.
        Extract the Email Address and Phone Number from the provided CV document.
        
        If multiple found, prefer the most prominent one.
        If none found, return empty string.
        
        Output valid JSON.
        """
        super().__init__(
            llm=llm,
            prompt_template=prompt_template,
            output_model=CvContactOutput,
            use_structured_output=True,
            **kwargs
        )

    async def __call__(self, file_bytes: bytes, mime_type: str = "application/pdf") -> Dict[str, Any]:
        base64_data = base64.b64encode(file_bytes).decode('utf-8')
        
        message_content = [
            {"type": "text", "text": "Extract contact info from this CV."},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{base64_data}"}
            }
        ]
        
        raw, parsed = await self.arun_chain(input=message_content)
        return parsed.model_dump()

