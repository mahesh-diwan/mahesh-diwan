"""Design tokens — single source of truth for all profile art.

Every color, font, and layout constant used by generators lives here.
Change once, propagate everywhere.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    bg: str = "#0d1117"
    surface: str = "#161b22"
    fg: str = "#c9d1d9"
    muted: str = "#8b949e"
    cyan: str = "#00D4FF"
    green: str = "#27c93f"
    yellow: str = "#ffbd2e"
    red: str = "#ff5f56"
    font_stack: str = (
        '"Fragment Mono", "DM Mono", "Fira Code", '
        "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
    )
    font_url: str = (
        "https://fonts.googleapis.com/css2?"
        "family=DM+Mono:wght@400;500"
        "&family=Fragment+Mono:wght@400;500;700"
        "&display=swap"
    )

    @property
    def font_css(self) -> str:
        return (
            f'    @import url("{self.font_url}");\n'
            f"    text {{ font-family: {self.font_stack}; }}"
        )


THEME = Theme()
