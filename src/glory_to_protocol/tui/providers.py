from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial

from textual.command import Hit
from textual.command import Provider


class ExposedCommandProvider(Provider):
    """Feeds Textual's native command palette with `ExposedCommand` entries.

    Registered via `ProtocolApp.COMMANDS`; activated by the default `ctrl+\\`
    keybind. Picking a hit triggers the same FormScreen swap as selecting
    from the palette body.
    """

    async def search(self, query: str) -> AsyncIterator[Hit]:
        from glory_to_protocol.tui.app import ProtocolApp

        app = self.app
        if not isinstance(app, ProtocolApp):  # pragma: no cover - defensive
            return
        matcher = self.matcher(query)
        for command in app.protocol.exposed:
            haystack = f"{command.label} {command.section or ''} {command.description}".strip()
            score = matcher.match(haystack)
            if score <= 0:
                continue
            yield Hit(
                score,
                matcher.highlight(haystack),
                partial(app.activate_exposed_command, command),
                help=command.description or None,
            )
