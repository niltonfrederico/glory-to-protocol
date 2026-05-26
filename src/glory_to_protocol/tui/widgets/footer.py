from __future__ import annotations

from textual.widgets import Static

from glory_to_protocol.tui.identity import BureauTheme


class BindingsFooter(Static):
    DEFAULT_CSS = """
    BindingsFooter {
        dock: bottom;
        height: 1;
        background: $bg-tint;
        color: $muted;
        padding: 0 1;
    }
    """

    def __init__(self, theme: BureauTheme, bindings: list[tuple[str, str]]) -> None:
        self._theme = theme
        self._binding_specs = bindings
        super().__init__(self._render_text())

    def _render_text(self) -> str:
        labels = self._theme.footer_labels
        parts = [
            f"[{key}] {labels[action] if action in labels else action}"  # noqa: SIM401
            for key, action in self._binding_specs
        ]
        return "   ".join(parts)
