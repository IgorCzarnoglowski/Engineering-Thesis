import lmstudio as lms
from config.settings import LMS_MODEL


def chat(system_prompt: str, user_prompt: str, response_schema=None):
    model = lms.llm(LMS_MODEL)
    chat = lms.Chat(system_prompt)
    chat.add_user_message(user_prompt)

    kwargs = {}
    if response_schema is not None:
        kwargs["response_format"] = response_schema

    return model.respond(chat, **kwargs)
