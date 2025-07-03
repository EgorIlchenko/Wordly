from difflib import get_close_matches

from spellchecker import SpellChecker

spell = SpellChecker()


def validate_word(word: str) -> dict:
    word = word.lower()
    if word in spell:
        return {"correct": True, "suggestions": []}

    candidates = spell.candidates(word)

    suggestions = get_close_matches(word, candidates, n=3, cutoff=0.8)

    return {"correct": False, "suggestions": suggestions}
