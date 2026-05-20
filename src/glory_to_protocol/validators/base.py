def has_disallowed_characters(text: str, allowed_set: set[str]) -> tuple[bool, set[str]]:
    disallowed = {_char for _char in text if _char not in allowed_set}
    return not bool(disallowed), disallowed
