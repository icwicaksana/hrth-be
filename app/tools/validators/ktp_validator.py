import base64
from typing import Dict, Any, Union
from core.BaseAgent import BaseAgent
from pydantic import BaseModel, Field

class KtpValidationOutput(BaseModel):
    is_valid: bool = Field(..., description="True if KTP is valid, clearly visible, and contains necessary fields.")
    nik: str = Field(..., description="Extracted NIK number.")
    full_name: str = Field(..., description="Extracted Full Name.")
    address: str = Field(..., description="Extracted Address (Alamat) fully.")
    gender: str = Field(..., description="Extracted Gender (Jenis Kelamin).")
    birth_place: str = Field(..., description="Extracted Birth Place (Tempat Lahir).")
    birth_date: str = Field(..., description="Extracted Birth Date (Tanggal Lahir) in DD-MM-YYYY format.")
    reasoning: str = Field(..., description="Reasoning for validity status.")

class KtpValidator(BaseAgent):
    def __init__(self, llm, **kwargs):
        prompt_template = """
        You are an Identity Verification Expert. Analyze the provided KTP image/document.
        
        Task:
        1. Check if the image is a valid Indonesian KTP (Kartu Tanda Penduduk).
        2. Ensure NIK, Name, Address, Gender, and Birth Date are clearly visible.
        3. Extract the following fields:
           - NIK
           - Full Name
           - Address
           - Gender (Laki-Laki / Perempuan)
           - Birth Place (Tempat Lahir)
           - Birth Date (Tanggal Lahir)
        
        Output valid JSON matching the schema.
        """
        super().__init__(
            llm=llm,
            prompt_template=prompt_template,
            output_model=KtpValidationOutput,
            use_structured_output=True,
            **kwargs
        )

    async def __call__(self, file_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        # Encode bytes to base64
        base64_data = base64.b64encode(file_bytes).decode('utf-8')
        
        # Prepare Multimodal Input
        message_content = [
            {"type": "text", "text": "Analyze this KTP document."},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{base64_data}"}
            }
        ]
        
        # Run Chain
        raw, parsed = await self.arun_chain(input=message_content)
        return parsed.model_dump()
