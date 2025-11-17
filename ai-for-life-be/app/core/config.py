from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Gemini AI
    GEMINI_API_KEY: str = "AIzaSyBaKm-HcRs0oThVyi95MxnJzNuvYztIids"
    
    # App settings
    APP_NAME: str = "JobMatcherAPI"
    APP_DEBUG: bool = True

    # ChromaDB settings
    CHROMA_DB_PATH: str = "./.chroma"
    CHROMA_COLLECTION_JOBS: str = "jobs"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
