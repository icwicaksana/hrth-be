import base64
from typing import Dict, Any
from core.BaseAgent import BaseAgent
from pydantic import BaseModel, Field

class CriminalExtractionOutput(BaseModel):
    is_valid: bool = Field(..., description="True if the SKCK/Criminal Record is valid and signature is present.")
    full_name: str = Field(..., description="Name extracted from the document.")
    status: str = Field(..., description="Status of criminal record (e.g. CLEAN, NOT CLEAN).")
    has_signature: bool = Field(..., description="True if a valid signature is detected.")
    reasoning: str = Field(..., description="Reasoning for validity.")

class CriminalValidator(BaseAgent):
    def __init__(self, llm, **kwargs):
        prompt_template = """
        You are a Legal Document Expert. Analyze the SKCK (Criminal Record Certificate) document.
        
        Task:
        1. Extract the Name and Criminal Status.
        2. Check if the document is signed (look for signature/stamp).
        3. Verify if the Name matches the candidate's name: {candidate_name}
        
        Output valid JSON.
        """
        super().__init__(
            llm=llm,
            prompt_template=prompt_template,
            output_model=CriminalExtractionOutput,
            use_structured_output=True,
            **kwargs
        )

    async def __call__(self, file_bytes: bytes, candidate_name: str, mime_type: str = "application/pdf") -> Dict[str, Any]:
        base64_data = base64.b64encode(file_bytes).decode('utf-8')
        
        self.rebind_prompt_variable(candidate_name=candidate_name)
        
        message_content = [
            {"type": "text", "text": "Analyze this criminal record document."},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{base64_data}"}
            }
        ]
        
        raw, parsed = await self.arun_chain(input=message_content)
        return parsed.model_dump()

