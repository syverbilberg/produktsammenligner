"""Shown when the products are of unrelated types (phone vs robot vacuum):
a clear warning with a choice, and the side-by-side overview."""
from __future__ import annotations

from html import escape

import streamlit as st

from src.comparison import MISSING, kr
from src.insights.overview import build_overview
from src.ui import state
from src.ui.components import card_title, html

LETTERS = "ABCD"


def render_choice(compat) -> None:
    """The warning card in the steps column, replacing the priority step."""
    with st.container(key="card_mismatch"):
        card_title("scale", "Ulike produkttyper")
        html(f'<div class="ps-warning big">{escape(compat.message)}</div>')
        if st.session_state.side_by_side:
            html('<div class="ps-hint">Viser produktene side om side – uten vinner eller poeng.</div>')
        html('<div class="ps-sub">Hva vil du gjøre?</div>')
        for index in compat.odd_ones:
            st.button(f"Bytt produkt {LETTERS[index]}", key=f"replace_{index}", on_click=state.replace_product,
                      args=(index,), use_container_width=True)
        if not st.session_state.side_by_side:
            st.button("Vis likevel side om side", key="show_side_by_side", type="primary",
                      on_click=state.show_side_by_side, use_container_width=True)


def render_overview(key: str) -> None:
    """Side-by-side cards, one per product. `key` keeps widget keys unique per tab."""
    overviews = build_overview(list(st.session_state.products))
    with st.container(key=f"card_overview_{key}"):
        card_title("grid", "Side om side")
        html('<div class="ps-hint" style="margin:-4px 0 12px">Ulike produkttyper – hvert produkt vises for seg, '
             "uten vinner. Nyttig hvis kunden velger mellom to kjøp med samme budsjett.</div>")
        cards = ""
        for i, ov in enumerate(overviews):
            p = ov.product
            image = f'<img src="{escape(p.image)}">' if p.image else '<div class="ps-noimg"></div>'
            rating = (f'<div class="ps-rating">★ {p.rating:.1f}'.replace(".", ",")
                      + (f" ({p.review_count})" if p.review_count else "") + "</div>") if p.rating else ""
            specs = "".join(f"<tr><td>{escape(label)}</td><td>{escape(value)}</td></tr>" for label, value in ov.specs)
            features = "".join(f"<li>{escape(f)}</li>" for f in ov.features)
            included = f'<div class="ps-sub">Følger med</div><div>{escape(", ".join(ov.included))}</div>' if ov.included else ""
            cards += (
                f'<div class="ps-ov"><div class="head">{image}<div><span class="ps-badge sm">{LETTERS[i]}</span>'
                f'<a class="name" href="{escape(p.url)}" target="_blank">{escape(ov.short_name)}</a>'
                f'<div class="meta">{escape(ov.category_name)}</div>'
                f'<div class="price">{kr(p.price) if p.price else MISSING}</div>{rating}</div></div>'
                + (f'<div class="ps-sub">Nøkkelinfo</div><table class="ps-ovtable">{specs}</table>' if specs else "")
                + (f'<div class="ps-sub">Funksjoner</div><ul class="ps-ovlist">{features}</ul>' if features else "")
                + included + "</div>"
            )
        html(f'<div class="ps-ovs">{cards}</div>')
