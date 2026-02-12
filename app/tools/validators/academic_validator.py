import base64
import asyncio
from typing import Dict, Any

from pddiktipy import api as pddikti_api
from core.BaseAgent import BaseAgent
from pydantic import BaseModel, Field

class AcademicExtractionOutput(BaseModel):
    full_name: str = Field(..., description="Name extracted from the certificate.")
    university: str = Field(..., description="University name extracted.")
    nomor_ijazah: str = Field(..., description="Certificate number (Nomor Ijazah).")

class AcademicValidator(BaseAgent):
    def __init__(self, llm, **kwargs):
        prompt_template = """
        You are an Academic Verification Expert. Extract key details from the Ijazah (Certificate).
        
        Extract:
        - Full Name
        - University Name
        - Nomor Ijazah
        
        Output valid JSON.
        """
        super().__init__(
            llm=llm,
            prompt_template=prompt_template,
            output_model=AcademicExtractionOutput,
            use_structured_output=True,
            **kwargs
        )

    async def __call__(self, file_bytes: bytes, mime_type: str = "application/pdf") -> Dict[str, Any]:
        # 1. Extract Data from Ijazah
        base64_data = base64.b64encode(file_bytes).decode('utf-8')
        message_content = [
            {"type": "text", "text": "Extract details from this academic certificate."},
            {
                "type": "image_url", # Gemini via LangChain handles PDF as image_url often or media
                "image_url": {"url": f"data:{mime_type};base64,{base64_data}"}
            }
        ]
        
        raw, parsed = await self.arun_chain(input=message_content)
        extracted = parsed.model_dump()
        
        # 2. Call PDDIKTI API
        api_data = await self._search_pddikti(extracted["full_name"])
        
        # 3. Compare (Simple logic for now, could use LLM for fuzzy match)
        is_valid = False
        reasoning = "PDDIKTI Data not found"
        matched_record = None
        
        if api_data:
            # Check if university matches vaguely
            uni_lower = extracted["university"].lower()
            
            # Find best match in api_data list
            for record in api_data:
                if record["nama_pt"].lower() in uni_lower or uni_lower in record["nama_pt"].lower():
                    matched_record = record
                    break
            
            if matched_record:
                is_valid = True
                reasoning = f"Verified against PDDIKTI. NIM: {matched_record.get('nim')}, PT: {matched_record.get('nama_pt')}"
            else:
                reasoning = f"Name found in PDDIKTI but University mismatch. Ijazah: {extracted['university']}"
        
        # 4. Transform response to match frontend schema format
        # Map PDDIKTI API fields (nama_pt, nama, nim, etc.) to frontend expected format
        return {
            "is_valid": is_valid,
            "university_name": matched_record.get("nama_pt", extracted["university"]) if matched_record else extracted["university"],
            "student_name": matched_record.get("nama", extracted["full_name"]) if matched_record else extracted["full_name"],
            "graduation_year": "",  # Extract from Ijazah if needed, or leave empty
            "gpa": 0.0,  # Extract from Ijazah if needed, or leave as default
            "reasoning": reasoning,
            # Keep raw data for debugging/reference if needed
            "extracted": extracted,
            "pddikti_data": api_data,
            "matched_record": matched_record  # Include matched record for reference
        }

    async def _search_pddikti(self, name: str) -> list:
        def _fetch() -> list:
            try:
                with pddikti_api() as client:
                    return client.search_mahasiswa(name)
            except Exception:
                return []

        return await asyncio.to_thread(_fetch)

