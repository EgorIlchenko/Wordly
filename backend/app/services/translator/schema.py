from typing import List

from pydantic import BaseModel


class Example(BaseModel):
    sentence: str
    meaning: str


class TranslationResponse(BaseModel):
    translations: List[str]
    examples: List[Example]
