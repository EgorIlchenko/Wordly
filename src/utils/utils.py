import random

from difflib import get_close_matches

from spellchecker import SpellChecker

from core.config import CODE_LENGTH, NUMBER_OF_MATCHES, CUTOFF

spell = SpellChecker()


def validate_word(word: str) -> dict:
    word = word.lower()
    if word in spell:
        return {"correct": True, "suggestions": []}

    candidates = spell.candidates(word=word)

    suggestions = get_close_matches(
        word=word,
        possibilities=candidates,
        n=NUMBER_OF_MATCHES,
        cutoff=CUTOFF,
    )

    return {"correct": False, "suggestions": suggestions}


def camel_case_to_snake_case(input_str: str) -> str:
    chars = []
    for c_idx, char in enumerate(input_str):
        if c_idx and char.isupper():
            nxt_idx = c_idx + 1
            flag = nxt_idx >= len(input_str) or input_str[nxt_idx].isupper()
            prev_char = input_str[c_idx - 1]
            if prev_char.isupper() and flag:
                pass
            else:
                chars.append("_")
        chars.append(char.lower())
    return "".join(chars)


def generate_code() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(CODE_LENGTH))