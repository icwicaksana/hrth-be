import logging

from config.supabase import supabase_client
from app.services.PapiService import PapiService
from app.schemas.PapiSchemas import PapiScoringRequest, PapiScoringResponse

logger = logging.getLogger(__name__)

class PapiController:
    def __init__(self):
        self.service = PapiService()

    async def score_candidate(self, request: PapiScoringRequest, user_id: str) -> PapiScoringResponse:
        # 1. Calculate Scores
        scores = self.service.calculate_scores(request.answers)
        
        # 2. Get Interpretations
        interpretations = self.service.get_interpretation(scores)
        
        # 3. Generate AI Summary (Strengths & Weaknesses)
        strengths, weaknesses = await self.service.generate_summary(scores, interpretations)
        
        # 4. Generate Summary Image
        image_base64 = self.service.generate_image(request.candidate_name, request.email, strengths, weaknesses)
        
        # 5. Return Response
        response = PapiScoringResponse(
            scores=scores,
            interpretations=interpretations,
            strengths=strengths,
            weaknesses=weaknesses,
            summary_image=image_base64
        )

        # 6. Log Activity
        try:
            log_data = {
                "user_id": user_id,
                "tool_type": "papi_scoring",
                "input_files": [],
                "output_files": [],
                "result_json": {
                    "candidate_name": request.candidate_name,
                    "email": str(request.email),
                    "scores": response.scores,
                    "interpretations": response.interpretations,
                    "strengths": response.strengths,
                    "weaknesses": response.weaknesses,
                    "summary_image": response.summary_image
                },
                "cost_usd": 0,
                "token_usage": {}
            }
            supabase_client.table("activity_logs").insert(log_data).execute()
        except Exception as e:
            logger.error(f"PAPI logging failed: {str(e)}")

        return response

