import logging
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field

parent_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(dotenv_path=parent_dir+"/.env")


class Settings(BaseSettings):
    MODEL_NAME: str = "meta-llama/Llama-4-Scout-17B-16E-Instruct" # "deepseek-r1-distill-llama-70b"
    REASONING: bool = False  # True
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.3
    TIMEOUT: float = 30.0  # groq is fast
    TOP_P: float = 0.95
    STREAM: bool = False
    MAX_RETERIES: int = 2
    GROQ_API_KEY: Optional[str] = None
    GROQ_ENDPOINT: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s:%(lineno)d - %(message)s"
)
logger = logging.getLogger(__name__)

settings = Settings()

logger.info("Environment configuration loaded successfully")
