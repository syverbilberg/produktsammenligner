"""Page layout: header, the product-group tabs (MDA, SDA …), then two tabs.

«Anbefaling»: result on the left, steps on the right (same arrangement as
the subscription calculator). «Funksjoner og bruk»: features, use cases and
pros/cons for the fetched products, no priorities needed.
"""
import streamlit as st

from src.ui import group_tabs, insights_view, priority_step, product_step, result_view, state
from src.ui.components import header, html
from src.ui.theme import CSS


def run() -> None:
    """Build the whole page."""
    st.set_page_config(page_title="Produktsammenligner", page_icon="⚖️", layout="wide")
    html(CSS)
    state.init()
    state.drop_stale_products()
    header()
    group_tabs.render()

    recommend_tab, features_tab = st.tabs(["Anbefaling", "Funksjoner og bruk"])
    with recommend_tab:
        result_col, steps_col = st.columns([1.15, 1], gap="large")
        with steps_col:
            product_step.render()
            priority_step.render()
        with result_col:
            result_view.render()
    with features_tab:
        insights_view.render()
