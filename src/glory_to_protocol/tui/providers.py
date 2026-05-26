from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial

from textual.command import DiscoveryHit
from textual.command import Hit
from textual.command import Provider
from textual.content import Content


class ExposedCommandProvider(Provider):
    """Feeds Textual's native command palette with `ExposedCommand` entries.

    Registered via `ProtocolApp.COMMANDS`; activated by the default `ctrl+\\`
    keybind. Picking a hit triggers the same FormScreen swap as selecting
    from the palette body.
    """

    async def discover(self) -> AsyncIterator[DiscoveryHit]:
        from glory_to_protocol.tui.app import ProtocolApp

        app = self.app
        if not isinstance(app, ProtocolApp):  # pragma: no cover - defensive
            return
        for index, command in enumerate(app.protocol.exposed, start=1):
            label = command.label or command.typer_name
            display = Content.from_markup(f"[dim]№{index:03d}[/dim]  ") + Content(label)
            yield DiscoveryHit(
                display,
                partial(app.activate_exposed_command, command),
                help=command.description or None,
            )

    async def search(self, query: str) -> AsyncIterator[Hit]:
        from glory_to_protocol.tui.app import ProtocolApp

        app = self.app
        if not isinstance(app, ProtocolApp):  # pragma: no cover - defensive
            return
        matcher = self.matcher(query)
        for index, command in enumerate(app.protocol.exposed, start=1):
            haystack = f"{command.label} {command.section or ''} {command.description}".strip()
            score = matcher.match(haystack)
            if score <= 0:
                continue
            prefix = Content.from_markup(f"[dim]№{index:03d}[/dim]  ")
            display = prefix + matcher.highlight(haystack)
            yield Hit(
                score,
                display,
                partial(app.activate_exposed_command, command),
                help=command.description or None,
            )
