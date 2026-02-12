import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Config
    APP_NAME: str
    APP_ENV: str
    APP_VERSION: str
    
    # Supabase Config
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    ALLOWED_ORIGINS: str
    
    # Groq Config
    GROQ_API_KEY: str
    
    # Google Cloud Config
    VERTEX_API_KEY: str
    GCP_PROJECT_ID: str
    
    # JWT Config
    JWT_HS_SECRET: str
    JWT_ROLES_INDEX: str

    # Docker Config
    DOCKER_CONTAINER_NAME: str
    DOCKER_PORTS: str
    DOCKER_WORKER_COUNT: int

    class Config:
        env_file = ".env"
        extra = "ignore"

env = Settings()
