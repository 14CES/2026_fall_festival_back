from korcen import korcen


def contains_forbidden_word(text: str) -> bool:
    return korcen.check(text)