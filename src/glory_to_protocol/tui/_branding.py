from __future__ import annotations

REPO_URL = "https://github.com/niltonfrederico/glory-to-protocol"
LINK_LABEL = "Glory to Protocol!"


def body_subtitle(repo_url: str = REPO_URL) -> str:
    return f'[link="{repo_url}"]{LINK_LABEL}[/link]'
