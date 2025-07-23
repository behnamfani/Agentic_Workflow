import os
from langchain_groq import ChatGroq

from src.config import settings, logger

os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

try:
    llm = ChatGroq(
        model=settings.MODEL_NAME,
        temperature=settings.TEMPERATURE,
        max_tokens=settings.MAX_TOKENS,
        reasoning_format="parsed",
        timeout=settings.TIMEOUT,
        max_retries=settings.MAX_RETERIES,
    )

    messages = [
        (
            "system",
            "You are a helpful assistant that translates English to French. Translate the user sentence. "
            "Then give me word to word translations",
        ),
        ("human", "I love programming and Pandas."),
    ]
    ai_msg = llm.invoke(messages)
    print(ai_msg)
except Exception as e:
    logger.error(f"Error at generating response: {e}")