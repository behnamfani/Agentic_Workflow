import os
from langchain_groq import ChatGroq

os.environ["GROQ_API_KEY"] = "..."

llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0.5,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
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