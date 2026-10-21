"""Step 1: the customer enters 2–4 varekoder or links and we fetch them."""
from __future__ import annotations

from html import escape

import streamlit as st

from src.categories import detect_category
from src.comparison import kr
from src.fetching import FetchError, InputError, fetch_product
from src.models import Product
from src.ui import state
from src.ui.components import card_title, html

LETTERS = "ABCD"


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_fetch(text: str) -> Product:
    """Fetch once per input per hour."""
    return fetch_product(text)


def _tile(product: Product) -> None:
    """Small confirmation tile under an input: image, name, price, category."""
    category = detect_category(product)
    meta = " · ".join(filter(None, [
        kr(product.price) if product.price else "Pris ikke oppgitt",
        category.name if category else "Ukjent kategori",
        f"{len(product.specs)} spesifikasjoner",
    ]))
    image = f'<img src="{escape(product.image)}">' if product.image else ""
    html(f'<div class="ps-tile">{image}<div><div class="name">{escape(product.name)}</div>'
         f'<div class="meta">{escape(meta)}</div></div></div>')


def _fetch_all() -> None:
    """Fetch every product and store them (or the errors) in session state."""
    inputs = state.current_inputs()
    products, errors = [], []
    for letter, text in zip(LETTERS, inputs):
        if not text:
            errors.append(f"Produkt {letter}: fyll inn en varekode eller lenke.")
            continue
        try:
            products.append(_cached_fetch(text))
        except (InputError, FetchError) as err:
            errors.append(f"Produkt {letter}: {err}")
    st.session_state.fetch_errors = errors
    if not errors:
        st.session_state.products = products
        st.session_state.fetched_for = inputs
        st.session_state.result = None


def render() -> None:
    """Draw the product card, '+ Legg til produkt' and the fetch button."""
    count = st.session_state.count
    products = st.session_state.products

    with st.container(key="card_products"):
        head, reset_col = st.columns([5, 1], vertical_alignment="center")
        with head:
            card_title("box", "Produktene som skal sammenlignes")
        with reset_col:
            st.button("↺ Ny", on_click=state.reset, use_container_width=True)

        for index in range(count):
            field, remove = st.columns([10, 1], vertical_alignment="bottom")
            with field:
                st.text_input(f"Produkt {LETTERS[index]}", key=state.input_key(index),
                              placeholder="Varekode (f.eks. 457340) eller lenke til elkjop.no")
            with remove:
                if count > state.MIN_PRODUCTS:
                    st.button("✕", key=f"remove_{index}", help="Fjern produktet",
                              on_click=state.remove_product, args=(index,))
            if products and index < len(products):
                _tile(products[index])

        if count < state.MAX_PRODUCTS:
            with st.container(key="add_product"):
                st.button("+ Legg til produkt", on_click=state.add_product, use_container_width=True)

    for error in st.session_state.fetch_errors:
        st.error(error)

    if not st.session_state.products:
        if st.button("Hent produkter →", type="primary", use_container_width=True):
            with st.spinner("Henter produktene fra Elkjøp …"):
                _fetch_all()
            st.rerun()
