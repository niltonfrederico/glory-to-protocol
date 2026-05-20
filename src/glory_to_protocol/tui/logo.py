from typing import Literal

from rich.style import Style
from rich.text import Text

LOGO_LARGE = """\
███╗   ██╗██╗██████╗ ██╗   ██╗██╗   ██╗████████╗███████╗██╗  ██╗██╗  ██╗
████╗  ██║██║██╔══██╗██║   ██║╚██╗ ██╔╝╚══██╔══╝██╔════╝██║ ██╔╝██║  ██║
██╔██╗ ██║██║██████╔╝██║   ██║ ╚████╔╝    ██║   █████╗  █████╔╝ ███████║
██║╚██╗██║██║██╔══██╗╚██╗ ██╔╝  ╚██╔╝     ██║   ██╔══╝  ██╔═██╗ ██╔══██║
██║ ╚████║██║██║  ██║ ╚████╔╝    ██║      ██║   ███████╗██║  ██╗██║  ██║
╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝  ╚═══╝     ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝\
"""

LOGO_SMALL = """\
╔═══════════════╗
║ ★ NIRVYTEKH ★ ║
╚═══════════════╝\
"""


LogoSize = Literal["large", "small"]


def render_logo(size: LogoSize, style: Style) -> Text:
    raw = LOGO_LARGE if size == "large" else LOGO_SMALL
    return Text(raw, style=style)
