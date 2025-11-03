import logging
import os
import sys
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field

parent_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(dotenv_path=parent_dir+"/.env")


class Settings(BaseSettings):
    # https://console.groq.com/docs/models https://console.groq.com/docs/reasoning
    MODEL_NAME: str = "meta-llama/Llama-4-Scout-17B-16E-Instruct"
    REASONING: bool = False  # True
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.7
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


# Create the default logger (existing logic)
_default_logger = logging.getLogger(__name__)
_default_logger.setLevel(logging.INFO)
# Prevent adding handlers multiple times (more robust check)
if not _default_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
    ))
    _default_logger.addHandler(handler)
# Prevent log propagation to avoid duplicate messages from parent loggers
_default_logger.propagate = False
logger = _default_logger

settings = Settings()

logger.info("Environment configuration loaded successfully")
