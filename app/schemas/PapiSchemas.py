from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Dict, Optional

class PapiScoringRequest(BaseModel):
    candidate_name: str = Field(..., description="Full name of the candidate")
    email: EmailStr = Field(..., description="Email of the candidate")
    answers: List[int] = Field(
        ..., 
        description="List of 90 answers (1 or 2)", 
        min_items=90, 
        max_items=90
    )

    @validator('answers')
    def validate_answers(cls, v):
        if not all(x in [1, 2] for x in v):
            raise ValueError('All answers must be either 1 or 2')
        return v

class PapiScoringResponse(BaseModel):
    scores: Dict[str, int] = Field(..., description="Scores for each of the 20 personality factors (G, L, I, T, V, S, R, D, C, E, N, A, P, X, B, O, Z, K, F, W)")
    interpretations: Dict[str, str] = Field(..., description="Interpretation for each factor based on score range")
    strengths: List[str] = Field(..., description="List of inferred strengths")
    weaknesses: List[str] = Field(..., description="List of inferred weaknesses")
    summary_image: str = Field(..., description="Base64 encoded image of the summary")

class PapiSummaryOutput(BaseModel):
    strengths: List[str] = Field(..., description="Daftar kekuatan kandidat.")
    weaknesses: List[str] = Field(..., description="Daftar kelemahan kandidat.")

