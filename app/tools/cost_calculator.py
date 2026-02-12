from typing import Dict, Any

class CostCalculator:
    # Pricing per 1M tokens (Example for Gemini 1.5 Flash)
    # Adjust based on actual pricing
    PRICING = {
        "gemini-1.5-flash": {
            "input": 0.35, # per 1M tokens
            "output": 1.05  # per 1M tokens
        },
        "whisper": {
            "per_minute": 0.006 # Example
        }
    }

    @staticmethod
    def calculate_llm_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
        pricing = CostCalculator.PRICING.get(model_name, CostCalculator.PRICING["gemini-1.5-flash"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return round(input_cost + output_cost, 6)

    @staticmethod
    def calculate_audio_cost(duration_seconds: float) -> float:
        minutes = duration_seconds / 60
        cost = minutes * CostCalculator.PRICING["whisper"]["per_minute"]
        return round(cost, 6)

