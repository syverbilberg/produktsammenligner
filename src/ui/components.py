"""Small HTML building blocks shared by the steps."""
from __future__ import annotations

from html import escape

import streamlit as st

# Simple line icons (24×24, stroke = currentColor).
ICONS = {
    "box": '<path d="M3 7l9-4 9 4-9 4-9-4z"/><path d="M3 7v10l9 4 9-4V7"/><path d="M12 11v10"/>',
    "sliders": '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/>'
               '<circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    "list": '<path d="M8 6h12M8 12h12M8 18h12"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/>'
            '<circle cx="4" cy="18" r="1"/>',
    "scale": '<path d="M12 3v18M5 21h14M6 7h12"/><path d="M6 7l-3 7a3 3 0 006 0zM18 7l-3 7a3 3 0 006 0z"/>',
    "grid": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/>'
            '<rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "thumbs": '<path d="M7 11v9H4v-9zM7 11l4-8a2 2 0 012 2v4h5.5a2 2 0 012 2.3l-1.2 7A2 2 0 0117.3 20H7"/>',
    "camera": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    "battery": '<rect x="3" y="7" width="16" height="10" rx="2"/><path d="M21 11v2M6 10v4M9 10v4"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/>',
    "bolt": '<path d="M13 3L5 14h6l-1 7 8-11h-6z"/>',
    "screen": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    "pen": '<path d="M4 20l4-1L19 8l-3-3L5 16zM14 7l3 3"/>',
    "heart": '<path d="M12 20s-7-4.5-7-10a4 4 0 017-2.6A4 4 0 0119 10c0 5.5-7 10-7 10z"/>',
    "volume": '<path d="M4 10v4h4l5 4V6L8 10zM16 9a4 4 0 010 6M18.5 6.5a7.5 7.5 0 010 11"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M16 4.5a3.5 3.5 0 010 7M18 14c2 .7 3 3 3 6"/>',
    "plug": '<path d="M9 3v5M15 3v5M6 8h12v3a6 6 0 01-12 0zM12 17v4"/>',
    "leaf": '<path d="M5 19c0-9 6-14 15-14 0 9-5 15-14 15M5 19l7-7"/>',
    "home": '<path d="M4 11l8-7 8 7v9H4zM10 20v-5h4v5"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5zM3 13l9 5 9-5"/>',
    "sparkle": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8zM19 16l.7 1.8 1.8.7-1.8.7L19 21l-.7-1.8-1.8-.7 1.8-.7z"/>',
    "cake": '<path d="M4 21h16v-7H4zM4 17c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5M8 14v-3M12 14v-3M16 14v-3M8 8v1M12 7v2M16 8v1"/>',
    "bread": '<path d="M5 20V11a4 4 0 01-1-7.5C6 2 9 3 12 3s6-1 8 .5A4 4 0 0119 11v9z"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/>',
    "cup": '<path d="M5 8h11v6a5 5 0 01-5 5h-1a5 5 0 01-5-5zM16 9h2a2.5 2.5 0 010 5h-2M8 3v2M11 3v2"/>',
}


def icon(name: str, size: int = 22, color: str = "currentColor") -> str:
    """Inline SVG for one of the icons above."""
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


def html(markup: str) -> None:
    """Render raw HTML."""
    st.markdown(markup, unsafe_allow_html=True)


def header() -> None:
    """Full-width dark header bar."""
    html(f"""
    <div class="ps-header">
      <div class="ps-burger"><span></span><span></span><span></span></div>
      <div class="ps-mark">{icon("scale", 22, "#ffffff")}</div>
      <div>
        <div class="ps-title">Produktsammenligner</div>
        <div class="ps-subtitle">Elkjøp · varekode eller lenke · ærlig anbefaling</div>
      </div>
    </div>""")


def card_title(icon_name: str, title: str) -> None:
    """Icon box + bold title at the top of a card."""
    html(f'<div class="ps-card-head"><div class="ps-icon">{icon(icon_name)}</div>'
         f'<h3 class="ps-card-title">{escape(title)}</h3></div>')


def chips(items: list[tuple[str, str]], off_values: tuple[str, ...] = ()) -> None:
    """Grey summary chips like 'Pris · Svært viktig'."""
    parts = "".join(
        f'<span class="ps-chip{" off" if value in off_values else ""}"><b>{escape(label)}</b> · {escape(value)}</span>'
        for label, value in items
    )
    html(f'<div class="ps-chips">{parts}</div>')
