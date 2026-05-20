from src.glory_to_protocol.settings import ProtocolSettings


def validate_allowed_characters(text: str, allowed_characters_set: set[str]) -> bool:
    if any(_char not in allowed_characters_set for _char in text):
        return False

    return True
