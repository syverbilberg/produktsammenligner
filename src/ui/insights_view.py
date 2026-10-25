"""The "Funksjoner og bruk" tab: differences, features, use cases,
pros/cons and who should choose what. Needs fetched products only."""
from __future__ import annotations

from html import escape

import streamlit as st

from src.comparison import MISSING, kr
from src.insights import build_insights
from src.insights.phrasing import shown
from src.models import Insights
from src.categories.compatibility import UNRELATED
from src.ui import mismatch_view, state
from src.ui.components import card_title, html, icon

LETTERS = "ABCD"


def _bold(text: str) -> str:
    """Escape text and turn **x** into <b>x</b>."""
    parts = escape(text).split("**")
    return "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts))


def _empty() -> None:
    with st.container(key="card_insights_empty"):
        html('<div class="ps-empty"><div class="big">Ingen produkter ennå</div>'
             "Legg inn produktene over og trykk «Hent produkter». "
             "Her ser du så funksjoner, bruksområder og fordeler/ulemper – uten å svare på prioriteringer.</div>")


def _header_cards(ins: Insights) -> None:
    cards = []
    for i, product in enumerate(ins.products):
        image = f'<img src="{escape(product.image)}">' if product.image else '<div class="ps-noimg"></div>'
        rating = (f'<span class="ps-rating">★ {product.rating:.1f}'.replace(".", ",")
                  + (f" ({product.review_count})" if product.review_count else "") + "</span>") if product.rating else ""
        price = kr(product.price) if product.price else MISSING
        cards.append(
            f'<div class="ps-mini">{image}<div><span class="ps-badge sm">{LETTERS[i]}</span>'
            f'<a class="name" href="{escape(product.url)}" target="_blank">{escape(ins.short_names[i])}</a>'
            f'<div class="price">{price}</div>{rating}</div></div>'
        )
    html(f'<div class="ps-minis">{"".join(cards)}</div>')


def _name_headers(ins: Insights) -> str:
    return "".join(f"<th>{LETTERS[i]} · {escape(n)}</th>" for i, n in enumerate(ins.short_names))


def _differences(ins: Insights) -> None:
    with st.container(key="card_differences"):
        card_title("list", "Viktigste forskjeller")
        if not ins.differences:
            st.write("Ingen tydelige forskjeller i spesifikasjonene.")
            return
        body = ""
        for row in ins.differences:
            cells = ""
            for i, value in enumerate(row.values):
                cls = "win" if row.winner == i else ("missing" if value is None else "")
                cells += f'<td class="{cls}">{escape(shown(row.rule, value) if value else MISSING)}</td>'
            body += f'<tr><td class="spec">{escape(row.rule.label.split(" (")[0])}</td>{cells}</tr>'
        html(f'<div class="ps-table-wrap"><table class="ps-table"><thead><tr><th>Egenskap</th>'
             f'{_name_headers(ins)}</tr></thead><tbody>{body}</tbody></table></div>')


def _features(ins: Insights) -> None:
    with st.container(key="card_features"):
        card_title("grid", "Funksjoner")
        if ins.features:
            body = ""
            for feature in ins.features:
                cells = ""
                details = feature.details or ("",) * len(feature.values)
                for value, extra in zip(feature.values, details):
                    note = f'<span class="ps-detail">{escape(extra)}</span>' if extra else ""
                    if value is True:
                        cells += f'<td><span class="ps-yes">✓</span>{note}</td>'
                    elif value is False:
                        cells += '<td><span class="ps-no">✕</span></td>'
                    else:
                        cells += '<td class="missing" title="Ikke nevnt på produktsiden">–</td>'
                note = f'<span class="ps-source">fra {feature.source}</span>' if feature.source else ""
                body += f'<tr><td class="spec">{escape(feature.label)}{note}</td>{cells}</tr>'
            html(f'<div class="ps-table-wrap"><table class="ps-table ps-features"><thead><tr><th>Funksjon</th>'
                 f'{_name_headers(ins)}</tr></thead><tbody>{body}</tbody></table></div>')
            html('<div class="ps-hint">✓ har · ✕ har ikke · – ikke nevnt på produktsiden</div>')
        if any(ins.included):
            items = "".join(
                f'<div><b>{LETTERS[i]}:</b> {escape(", ".join(things)) if things else "Ikke oppgitt"}</div>'
                for i, things in enumerate(ins.included)
            )
            html(f'<div class="ps-included"><div class="ps-sub">Følger med</div>{items}</div>')


def _use_cases(ins: Insights) -> None:
    if not ins.scenarios:
        return
    with st.container(key="card_use_cases"):
        card_title("star", "Hvilken passer best til …?")
        items = ""
        for result in ins.scenarios:
            if result.winner is None:
                badge = '<span class="ps-pill none">Omtrent likt</span>'
            else:
                badge = f'<span class="ps-pill">{LETTERS[result.winner]} · {escape(ins.short_names[result.winner])}</span>'
            facts = "; ".join(result.reasons)
            items += (f'<div class="ps-usecase"><div class="ps-icon">{icon(result.scenario.icon)}</div>'
                      f'<div><div class="title">{escape(result.scenario.title)} {badge}</div>'
                      f'<div class="facts">{escape(facts[0].upper() + facts[1:]) if facts else ""}.</div></div></div>')
        html(items)


def _pros_cons(ins: Insights) -> None:
    with st.container(key="card_pros_cons"):
        card_title("thumbs", "Fordeler og ulemper")
        blocks = ""
        for i, name in enumerate(ins.short_names):
            pros = "".join(f"<li>{escape(p)}</li>" for p in ins.pros[i]) or "<li class='none'>Ingen tydelige</li>"
            cons = "".join(f"<li>{escape(c)}</li>" for c in ins.cons[i]) or "<li class='none'>Ingen tydelige</li>"
            blocks += (f'<div class="ps-pc"><div class="head"><span class="ps-badge sm">{LETTERS[i]}</span>'
                       f'{escape(name)}</div><div class="ps-sub good">Fordeler</div><ul class="good">{pros}</ul>'
                       f'<div class="ps-sub bad">Ulemper</div><ul class="bad">{cons}</ul></div>')
        html(f'<div class="ps-pcs">{blocks}</div>')


def _choose(ins: Insights) -> None:
    with st.container(key="card_choose"):
        card_title("check", "Hvilken bør kunden velge?")
        html("".join(f'<div class="ps-choose">{_bold(text)}</div>' for text in ins.choose))
        html('<div class="ps-hint">Bygger kun på det som står på Elkjøps produktsider. '
             "«Nevnt bare for» betyr at den andre siden ikke sier noe om det – ikke at funksjonen mangler.</div>")


def render() -> None:
    """Draw the whole tab."""
    products = st.session_state.get("products")
    if not products:
        _empty()
        return
    compat = state.compatibility()
    if compat.level == UNRELATED:
        if st.session_state.side_by_side:
            mismatch_view.render_overview("features")
        else:
            with st.container(key="card_insights_mismatch"):
                card_title("scale", "Ulike produkttyper")
                html(f'<div class="ps-warning big">{escape(compat.message)}</div>'
                     '<div class="ps-hint">Velg «Bytt produkt» eller «Vis likevel side om side» i fanen Anbefaling.</div>')
        return
    ins = build_insights(list(products))
    if compat.message:
        html(f'<div class="ps-warning">{escape(compat.message)}</div>')
    _header_cards(ins)
    left, right = st.columns([1, 1], gap="large")
    with left:
        _differences(ins)
        _features(ins)
    with right:
        _use_cases(ins)
        _pros_cons(ins)
        _choose(ins)
