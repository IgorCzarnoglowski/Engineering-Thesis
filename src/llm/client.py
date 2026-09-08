from config.settings import LMS_MODEL
from src.llm.web_search import search_web


def chat(system_prompt: str, user_prompt: str, response_schema=None, use_web_search=False):
    import lmstudio as lms

    model = lms.llm(LMS_MODEL)
    conversation = lms.Chat(system_prompt)
    conversation.add_user_message(user_prompt)

    if use_web_search:
        act_result = model.act(conversation, tools=[search_web])
        if response_schema is None:
            return act_result.content
        structured_conversation = lms.Chat(system_prompt)
        structured_conversation.add_user_message(
            f"{user_prompt}\n\nAdditional web context:\n{act_result.content}"
        )
        return model.respond(structured_conversation, response_format=response_schema)

    kwargs = {}
    if response_schema is not None:
        kwargs["response_format"] = response_schema

    return model.respond(conversation, **kwargs)
