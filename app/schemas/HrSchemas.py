from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CvAnalysisOutput(BaseModel):
    score: int = Field(description="Score of the candidate (0-100)")
    match_analysis: bool = Field(description="Whether the candidate matches the job criteria")
    strengths: List[str] = Field(description="List of candidate's strengths")
    weaknesses: List[str] = Field(description="List of candidate's weaknesses")
    summary: str = Field(description="Brief summary of the analysis")

class BgCheckExtraction(BaseModel):
    is_valid: bool = Field(description="Validity of the document")
    reasoning: str = Field(description="Reasoning for validity")
    extracted_data: Dict[str, Any] = Field(description="Extracted key-value pairs")

class OnboardingExtraction(BaseModel):
    name: str = Field(description="Candidate Name")
    email: str = Field(description="Candidate Email")
    phone: str = Field(description="Candidate Phone")
    address: str = Field(description="Candidate Address")
    # Add other fields as needed

class InterviewAnalysisOutput(BaseModel):
    summary: str = Field(description="Ringkasan proses wawancara")
    quality: str = Field(description="Kualitas jawaban kandidat")
    strengths: List[str] = Field(description="Kelebihan kandidat")
    weaknesses: List[str] = Field(description="Kekurangan kandidat")
    conclusion: str = Field(description="Kesimpulan dan rekomendasi")

class KtpValidationOutput(BaseModel):
    is_valid: bool = Field(..., description="True if KTP is valid, clearly visible, and contains necessary fields.")
    nik: str = Field(..., description="Extracted NIK number.")
    full_name: str = Field(..., description="Extracted Full Name.")
    address: str = Field(..., description="Extracted Address.")
    reasoning: str = Field(..., description="Reasoning for validity status.")

class AcademicExtractionOutput(BaseModel):
    is_valid: bool = Field(..., description="True if document is valid.")
    university_name: str = Field(..., description="Extracted University Name.")
    student_name: str = Field(..., description="Extracted Student Name.")
    graduation_year: str = Field(..., description="Extracted Graduation Year.")
    gpa: float = Field(..., description="Extracted GPA.")
    reasoning: str = Field(..., description="Reasoning.")

class CriminalExtractionOutput(BaseModel):
    is_valid: bool = Field(..., description="True if document is valid.")
    candidate_name: str = Field(..., description="Extracted Candidate Name.")
    police_name: str = Field(..., description="Extracted Police Name/Signer.")
    reasoning: str = Field(..., description="Reasoning.")

class InterviewAnalysisRequest(BaseModel):
    file_path: str = Field(..., description="Path to the file in Supabase Storage (hr-files bucket)")
