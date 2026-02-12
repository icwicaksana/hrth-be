import app.schemas as schemas
from fastapi import APIRouter, UploadFile, File, Form, Body, Depends
from typing import List, Dict, Any
from app.schemas.HrSchemas import InterviewAnalysisRequest
from app.schemas.PapiSchemas import PapiScoringRequest

from app.controllers.SampleController import sampleController
from app.controllers.CvController import CvController
from app.controllers.BgCheckController import BgCheckController
from app.controllers.OnboardingController import OnboardingController
from app.controllers.InterviewController import InterviewController
from app.controllers.HistoryController import HistoryController
from app.controllers.CriminalLetterController import CriminalLetterController
from app.controllers.PapiController import PapiController

from app.middleware import JwtMiddleware, RoleMiddleware

import logging
logger = logging.getLogger(__name__)

router = APIRouter()
jwt = JwtMiddleware()

# Instantiate Controllers
cv_controller = CvController()
bg_controller = BgCheckController()
onboarding_controller = OnboardingController()
interview_controller = InterviewController()
history_controller = HistoryController()
criminal_letter_controller = CriminalLetterController()
papi_controller = PapiController()

# --- CV Analyzer ---
@router.post("/cv-analyze", tags=["CV Analyzer"])
async def analyze_cv(
    file: UploadFile = File(...),
    job_position_id: int = Form(...),
    token_payload: dict = Depends(jwt)
):
    user_id = token_payload.get("sub") or token_payload.get("id")
    return await cv_controller.analyze(file, job_position_id, user_id)

# --- Background Check ---
@router.post("/bg-check/analyze", tags=["Background Check"])
async def bg_check_analyze(
    file_ktp: UploadFile = File(...),
    file_ijazah: UploadFile = File(...),
    file_skck: UploadFile = File(...),
    job_position_id: int = Form(...),
    interview_passed: bool = Form(...),
    reference_checked: bool = Form(...),
    token_payload: dict = Depends(jwt)
):
    user_id = token_payload.get("sub") or token_payload.get("id")
    return await bg_controller.analyze(
        file_ktp, file_ijazah, file_skck, 
        job_position_id, interview_passed, reference_checked,
        user_id
    )

@router.post("/bg-check/generate", tags=["Background Check"])
async def bg_check_generate(
    data: Dict[str, Any] = Body(...),
    token_payload: dict = Depends(jwt)
):
    user_id = token_payload.get("sub") or token_payload.get("id")
    return await bg_controller.generate_doc(data, user_id)

# --- Onboarding ---
@router.post("/onboarding/analyze", tags=["Onboarding"])
async def onboarding_analyze(
    file_ktp: UploadFile = File(...),
    file_cv: UploadFile = File(...),
    job_position_id: int = Form(...),
    join_date: str = Form(...),
    token_payload: dict = Depends(jwt)
):
    user_id = token_payload.get("sub") or token_payload.get("id")
    return await onboarding_controller.analyze(file_ktp, file_cv, job_position_id, join_date, user_id)

@router.post("/onboarding/generate", tags=["Onboarding"])
async def onboarding_generate(
    data: Dict[str, Any] = Body(...),
    token_payload: dict = Depends(jwt)
):
    user_id = token_payload.get("sub") or token_payload.get("id")
    return await onboarding_controller.generate_doc(data, user_id)

# --- Criminal Letter ---
@router.post("/criminal-letter/analyze", tags=["Criminal Letter"])
async def criminal_letter_analyze(
    file_ktp: UploadFile = File(...),
    job_position_id: int = Form(...),
    token_payload: dict = Depends(jwt)
):
    user_id = token_payload.get("sub") or token_payload.get("id")
    return await criminal_letter_controller.analyze(file_ktp, job_position_id, user_id)

@router.post("/criminal-letter/generate", tags=["Criminal Letter"])
async def criminal_letter_generate(
    data: Dict[str, Any] = Body(...),
    token_payload: dict = Depends(jwt)
):
    user_id = token_payload.get("sub") or token_payload.get("id")
    return await criminal_letter_controller.generate_doc(data, user_id)

# --- Interview Analyzer ---
@router.post("/interview-analyze", tags=["Interview Analyzer"])
async def analyze_interview(
    request: InterviewAnalysisRequest = Body(...),
    token_payload: dict = Depends(jwt)
):
    user_id = token_payload.get("sub") or token_payload.get("id")
    return await interview_controller.analyze(request, user_id)

# --- History ---
@router.get("/history", tags=["History"])
async def get_history(limit: int = 50, offset: int = 0):
    return await history_controller.get_history(limit, offset)

@router.delete("/history/{log_id}", tags=["History"])
async def delete_history(log_id: str):
    return await history_controller.delete_history(log_id)

# --- PAPI Kostick ---
@router.post("/tools/papi-scoring", tags=["HR Tools"])
async def papi_scoring(
    request: PapiScoringRequest = Body(...),
    token_payload: dict = Depends(jwt)
):
    user_id = token_payload.get("sub") or token_payload.get("id")
    return await papi_controller.score_candidate(request, user_id)
