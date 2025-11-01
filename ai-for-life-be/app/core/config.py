from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    APP_NAME: str = "JobMatcherAPI"
    APP_DEBUG: bool = True
    DATABASE_URL: str  # bắt buộc cung cấp qua .env

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_mysql(cls, v: str) -> str:
        if not v or not v.startswith("mysql+"):
            raise ValueError(
                "DATABASE_URL must be a MySQL URL, e.g. mysql+pymysql://USER:PASS@HOST:3306/DBNAME"
            )
        return v

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()
