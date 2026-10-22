"""Step 2: what matters most to the customer. Only shown after fetching,
and only asks about dimensions the two products can actually be compared on."""
from __future__ import annotations

import streamlit as st

from src.categories import dimensions as d
from src.comparison import compare, relevant_dimensions
from src.categories.compatibility import UNRELATED
from src.ui import mismatch_view, state
from src.ui.components import card_title, chips, html

_OPTIONS = list(d.LEVELS)


def _toggle() -> None:
    st.session_state.priorities_open = not st.session_state.priorities_open


def _run_comparison(dimensions: list[str]) -> None:
    """Compare with the chosen weights and collapse the priority card."""
    weights = state.weights(dimensions)
    st.session_state.result = compare(st.session_state.products, weights)
    st.session_state.priorities_open = False


def render() -> None:
    """Draw the priority card and the recommendation button."""
    products = st.session_state.products
    if not products:
        return
    compat = state.compatibility()
    if compat.level == UNRELATED:
        mismatch_view.render_choice(compat)   # no priorities: there is nothing to weigh
        return
    dimensions = relevant_dimensions(products)
    levels = st.session_state.levels
    # Read widget values first so the chips are up to date in this run.
    for dim in dimensions:
        widget_value = st.session_state.get(f"level_{dim}")
        if widget_value:
            levels[dim] = widget_value

    with st.container(key="card_priorities"):
        head, toggle_col = st.columns([5, 1.1], vertical_alignment="center")
        with head:
            card_title("sliders", "Hva er viktigst for kunden?")
        with toggle_col:
            st.button("Skjul" if st.session_state.priorities_open else "Endre", key="toggle_priorities",
                      on_click=_toggle, width="stretch")

        chips([(dim, levels.get(dim, d.DEFAULT_LEVEL)) for dim in dimensions], off_values=("Ikke viktig",))

        if st.session_state.priorities_open:
            for dim in dimensions:
                html(f'<div class="ps-dim-label">{dim}</div>')
                choice = st.segmented_control(
                    dim, _OPTIONS, default=levels.get(dim, d.DEFAULT_LEVEL),
                    key=f"level_{dim}", label_visibility="collapsed",
                )
                levels[dim] = choice or d.DEFAULT_LEVEL

    if st.session_state.result is None:
        # First time: one clear button. Afterwards only "Endre" is shown.
        st.button("Gi anbefaling →", type="primary", width="stretch",
                  on_click=_run_comparison, args=(dimensions,))
    else:
        # The recommendation follows the levels live, so "Endre" + a new
        # choice updates it at once without pressing anything else.
        st.session_state.result = compare(products, state.weights(dimensions))
