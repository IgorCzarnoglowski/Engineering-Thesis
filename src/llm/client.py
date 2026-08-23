import ollama
from config.settings import OLLAMA_MODEL


def chat(prompt: str) -> str:
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"].strip()
