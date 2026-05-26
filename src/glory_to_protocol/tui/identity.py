from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

StatusKey = Literal["ready", "working", "done", "error", "cancelled"]
FooterKey = Literal["quit", "help", "palette", "select", "back", "filter"]

DEFAULT_STATUS_STRINGS: dict[str, str] = {
    "ready": "Готов",
    "working": "В работе",
    "done": "Выполнено",
    "error": "Ошибка",
    "cancelled": "Отменено",
}

DEFAULT_FOOTER_LABELS: dict[str, str] = {
    "quit": "quit",
    "help": "help",
    "palette": "palette",
    "select": "select",
    "back": "back",
    "filter": "filter",
}


class BureauTheme(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field("NIRVYTEKH")
    subtitle: str = Field("Bureau of Computational Technology")
    logo_text: str = Field("NIRVYTEKH")
    accent: str = Field("#ffd84d")
    gold: str = Field("#ffe066")
    bg: str = Field("#0e0a05")
    border: str = Field("#7a5520")
    muted: str = Field("#b88040")
    text_color: str = Field("#ffb000")
    status_strings: dict[str, str] = Field(default_factory=lambda: dict(DEFAULT_STATUS_STRINGS))
    footer_labels: dict[str, str] = Field(default_factory=lambda: dict(DEFAULT_FOOTER_LABELS))
    directive_prefix: str = Field("ДИРЕКТИВА №")
    sign_off: str = Field("S chestyu, NIRVYTEKH")
