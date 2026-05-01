from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Advanced FastAPI MongoDB CRUD"
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "fastapi_db"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
