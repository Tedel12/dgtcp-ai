from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/dgtcp_ai"

    # JWT
    SECRET_KEY: str = "dgtcp_secret_key_2025_tres_longue_et_complexe"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # App
    APP_NAME: str = "DGTCP-AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Seuils de détection IA
    SEUIL_MONTANT_ELEVE: float = 500_000_000       # 500M FCFA
    SEUIL_SCORE_RISQUE_ELEVE: float = 75.0
    SEUIL_SCORE_RISQUE_MOYEN: float = 40.0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
