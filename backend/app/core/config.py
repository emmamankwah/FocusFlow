from pathlib import Path  #Imports a class that allow safe work in a folder directory

from pydantic import AliasChoices, Field         # The imported classes create a settings class that can read values from the .env file 
from pydantic_settings import BaseSettings, SettingsConfigDict

#Paths used in locating the .env file
BASE_DIR = Path(__file__).resolve().parents[2]   
PROJECT_ROOT = Path(__file__).resolve().parents[3]

#This class reads values from the .env file
class Settings(BaseSettings):
    PROJECT_NAME: str = "FocusFlow API"
    API_V1_STR: str = "/api/v1"

    #Access token remains valid for 15 minutes 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: str = "http://localhost:3000"
    
    #Values required to form the Database URL
    DB_USER: str = Field(default="root", validation_alias=AliasChoices("DB_USER", "USER"))
    DB_PASSWORD: str = Field(default="password", validation_alias=AliasChoices("DB_PASSWORD", "PASSWORD"))
    DB_HOST: str = Field(default="localhost", validation_alias=AliasChoices("DB_HOST", "HOST"))
    DB_PORT: str = Field(default="3306", validation_alias=AliasChoices("DB_PORT", "PORT"))
    DB_NAME: str = Field(default="Focus_Flow_AI", validation_alias=AliasChoices("DB_NAME", "DB"))
    SMTP_HOST:str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    OTP_OUTBOX_ENCRYPTION_KEY: str | None = None
    #Database URL is formed by this function
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  #The URL generated used by the session layer to access the database

    model_config = SettingsConfigDict(
        env_file=[
            BASE_DIR / ".env",
             PROJECT_ROOT / ".env"
             ],
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
