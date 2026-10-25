"""Step 3: the recommendation, summaries and the spec table."""
from __future__ import annotations

from html import escape

import numpy as np
import pandas as pd
import streamlit as st

from src.comparison import MISSING, kr
from src.insights.phrasing import shown
from src.models import ComparisonResult, Product
from src.categories.compatibility import UNRELATED
from src.ui import mismatch_view, state
from src.ui.components import card_title, html

LETTERS = "ABCD"


def _bold(text: str) -> str:
    """Escape text and turn **x** into <b>x</b>."""
    parts = escape(text).split("**")
    return "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts))


def _empty_state() -> None:
    with st.container(key="card_empty"):
        html("""
        <div class="ps-empty">
          <div class="big">Resultatet vises her</div>
          Legg inn to produkter, velg hva som er viktigst, og få en anbefaling.
          <div class="ps-steps"><span><b>1</b>Produkter</span><span><b>2</b>Prioriteringer</span>
          <span><b>3</b>Anbefaling</span></div>
        </div>""")


def _product_card(index: int, product: Product, result: ComparisonResult, best: int | None) -> str:
    category = result.categories[index]
    image = f'<img src="{escape(product.image)}">' if product.image else ""
    price = kr(product.price) if product.price else MISSING
    meta = f"{category.name if category else 'Ukjent kategori'} · {result.scores[index]:.0f} poeng"
    best_badge = '<span class="ps-best">Anbefalt</span>' if best == index else ""
    return (
        f'<div class="ps-product{" best" if best == index else ""}">{best_badge}'
        f'<span class="ps-badge">{LETTERS[index]}</span>{image}'
        f'<div class="name"><a href="{escape(product.url)}" target="_blank">{escape(product.name)}</a></div>'
        f'<div class="price">{price}</div><div class="meta">{escape(meta)}</div>'
        f'<div class="summary">{escape(result.summaries[index])}</div></div>'
    )


def _spec_table(result: ComparisonResult) -> str:
    rows = []
    for row in result.rows:
        cells = []
        for index, value in enumerate(row.values):
            if value is None:
                cells.append(f'<td class="missing">{MISSING}</td>')
            else:
                cls = ' class="win"' if row.winner == index else ""
                source = row.sources[index] if index < len(row.sources) else ""
                note = f'<span class="ps-source">fra {source}</span>' if source else ""
                cells.append(f"<td{cls}>{escape(shown(row.rule, value))}{note}</td>")
        if row.rule.kind == "info":
            pill = '<span class="ps-pill none">Info</span>'
        elif row.winner is None:
            same = row.values[0] is not None and len(set(row.values)) == 1
            pill = f'<span class="ps-pill none">{"Likt" if same else "–"}</span>'
        else:
            pill = f'<span class="ps-pill">{LETTERS[row.winner]}</span>'
        rows.append(f'<tr><td class="spec">{escape(row.rule.label)}</td>{"".join(cells)}'
                    f'<td>{pill}</td><td class="why">{escape(row.rule.why)}</td></tr>')
    letters = "".join(f"<th>{LETTERS[i]}</th>" for i in range(len(result.products)))
    return ('<div class="ps-table-wrap"><table class="ps-table"><thead><tr><th>Spesifikasjon</th>'
            f'{letters}<th>Vinner</th><th>Hvorfor det betyr noe</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def _all_specs_frame(products: list[Product]) -> pd.DataFrame:
    """Every spec from both pages; missing values as np.nan."""
    labels = list(dict.fromkeys([*products[0].specs, *products[1].specs]))
    return pd.DataFrame(
        {f"{LETTERS[i]}: {p.name}": [p.specs.get(label, np.nan) for label in labels] for i, p in enumerate(products)},
        index=labels,
    )


def render() -> None:
    """Draw the result column (or the empty state)."""
    compat = state.compatibility()
    if compat and compat.level == UNRELATED:
        if st.session_state.side_by_side:
            mismatch_view.render_overview("recommend")
        else:
            with st.container(key="card_empty_mismatch"):
                html('<div class="ps-empty"><div class="big">Ulike produkttyper</div>'
                     "Velg om du vil bytte produkt eller se dem side om side.</div>")
        return
    result: ComparisonResult | None = st.session_state.result
    if result is None:
        _empty_state()
        return

    top = max(result.scores)
    leaders = [i for i, s in enumerate(result.scores) if s == top]
    best = leaders[0] if len(leaders) == 1 else None

    with st.container(key="card_result"):
        card_title("star", "Anbefaling")
        for warning in result.warnings:
            html(f'<div class="ps-warning">{escape(warning)}</div>')
        html(f'<div class="ps-verdict">{_bold(result.verdict)}</div>')
        html('<div class="ps-products">'
             + "".join(_product_card(i, p, result, best) for i, p in enumerate(result.products))
             + "</div>")

    with st.container(key="card_table"):
        card_title("list", "Hva er egentlig forskjellen?")
        if result.rows:
            html(_spec_table(result))
        else:
            st.write("Fant ingen av de viktige spesifikasjonene på produktsidene.")
        with st.expander("Alle spesifikasjoner fra Elkjøp"):
            st.dataframe(_all_specs_frame(result.products), width="stretch")
