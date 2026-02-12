import logging

from groq import Groq
from langchain_google_genai import ChatGoogleGenerativeAI

from config.setting import env

logger = logging.getLogger(__name__)

class LLMFactory:
    _instance = None
    _groq_instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            logger.info("Initializing Google Gen AI LLM instance...")
            cls._instance = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                api_key=env.VERTEX_API_KEY,
                vertexai=True,
                temperature=1,
            )
        return cls._instance

    @classmethod
    def get_groq_client(cls):
        if cls._groq_instance is None:
            logger.info("Initializing Groq Client...")
            cls._groq_instance = Groq(api_key=env.GROQ_API_KEY)
        return cls._groq_instance

def get_llm():
    return LLMFactory.get_instance()

def get_groq():
    return LLMFactory.get_groq_client()
