import asyncio
import json
from typing import Optional

from langchain.schema import HumanMessage
from langchain_groq import ChatGroq

from backend.app.core.config import get_settings
from backend.app.services.translator.schema import TranslationResponse

settings = get_settings()

GROQ_API_KEY = settings.LLM_API_KEY


async def translate_word(word: str) -> Optional[TranslationResponse]:
    def sync_call():
        llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.3-70b-versatile")
        prompt = settings.TRANSLATION_PROMPT.format(word=word)
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()

    result = await asyncio.get_event_loop().run_in_executor(None, sync_call)

    try:
        parsed = json.loads(result)
        return TranslationResponse(**parsed)
    except Exception:
        return None
