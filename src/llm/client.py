import os
import time

from dotenv import load_dotenv
from openrouter import OpenRouter
from openrouter.errors import TooManyRequestsResponseError

from config.settings import OPENROUTER_MODEL

load_dotenv()

_client = OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY"))


def chat(system_prompt: str, user_prompt: str, response_schema=None, use_web_search=False):
    """Returns message content as str (JSON string when response_schema is a pydantic model)."""
    kwargs = {}
    if response_schema is not None:
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": response_schema.__name__,
                "strict": True,
                "schema": response_schema.model_json_schema(),
            },
        }

    # ":online" suffix = OpenRouter built-in web search, replaces local DDGS tool loop
    model = f"{OPENROUTER_MODEL}:online" if use_web_search else OPENROUTER_MODEL

    for attempt in range(6):
        try:
            response = _client.chat.send(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=False,
                **kwargs,
            )
            return response.choices[0].message.content
        except TooManyRequestsResponseError:
            if attempt == 5:
                raise
            time.sleep(2 ** attempt)  # 1,2,4,8,16s
