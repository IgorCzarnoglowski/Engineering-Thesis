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
    for attempt in range(6):
        try:
            if use_web_search:
                response = _client.responses.send(
                    model=OPENROUTER_MODEL,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    tools=[{"type": "openrouter:web_search"}],
                )
                message = next(
                    item for item in reversed(response.output) if item.type == "message"
                )
                return next(
                    part.text for part in message.content if part.type == "output_text"
                )
            else:
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
                response = _client.chat.send(
                    model=OPENROUTER_MODEL,
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
            return None
    return None
