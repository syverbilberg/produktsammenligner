"""Session state: what has been fetched and decided so far.

Flow: inputs → fetched products → priorities → result. Changing an input
after fetching clears everything downstream.
"""
from __future__ import annotations

import streamlit as st

from src.categories import dimensions as d

MIN_PRODUCTS = 2
MAX_PRODUCTS = 4

_DEFAULTS = {
    "count": MIN_PRODUCTS,     # number of product fields shown
    "products": None,          # list[Product] once fetched
    "fetched_for": None,       # the inputs the products belong to
    "fetch_errors": [],        # list[str]
    "levels": {},              # dimension -> level name ("Nøytral", …)
    "priorities_open": True,   # priority card expanded?
    "result": None,            # ComparisonResult
    "side_by_side": False,     # customer chose "Vis likevel side om side" for unrelated products
    "wrong_tab": None,         # group id suggested when a product belongs to another tab
}

DEFAULT_GROUP = "mda"


def input_key(index: int) -> str:
    """Widget key for product field number `index` (0-based)."""
    return f"input_{index}"


def init() -> None:
    """Create missing keys with defaults."""
    for key, value in _DEFAULTS.items():
        st.session_state.setdefault(key, value.copy() if isinstance(value, (list, dict)) else value)
    st.session_state.setdefault("group", DEFAULT_GROUP)


def set_group(group_id: str, keep_inputs: bool = False) -> None:
    """Open another tab. Normally starts over; `keep_inputs` keeps what is typed
    (used by "Bytt til fanen …" so the customer does not have to retype)."""
    typed = {k: v for k, v in st.session_state.items() if str(k).startswith("input_")} if keep_inputs else {}
    count = st.session_state.get("count", MIN_PRODUCTS)
    reset()
    st.session_state.group = group_id
    if keep_inputs:
        st.session_state.count = count
        for key, value in typed.items():
            st.session_state[key] = value


def reset() -> None:
    """Start a new comparison ("↺ Ny"). The open tab is kept."""
    for key, value in _DEFAULTS.items():
        st.session_state[key] = value.copy() if isinstance(value, (list, dict)) else value
    for key in [k for k in st.session_state if str(k).startswith(("input_", "level_"))]:
        del st.session_state[key]


def add_product() -> None:
    """Show one more product field (max 4)."""
    st.session_state.count = min(st.session_state.count + 1, MAX_PRODUCTS)


def remove_product(index: int) -> None:
    """Remove field `index` and shift the ones below it up."""
    count = st.session_state.count
    for i in range(index, count - 1):
        st.session_state[input_key(i)] = st.session_state.get(input_key(i + 1), "")
    st.session_state.pop(input_key(count - 1), None)
    st.session_state.count = max(count - 1, MIN_PRODUCTS)


def current_inputs() -> tuple[str, ...]:
    """What is typed in the product fields right now."""
    return tuple(st.session_state.get(input_key(i), "").strip() for i in range(st.session_state.count))


def drop_stale_products() -> None:
    """Forget fetched products if the inputs have changed since fetching."""
    if st.session_state.fetched_for and st.session_state.fetched_for != current_inputs():
        st.session_state.products = None
        st.session_state.result = None
        st.session_state.priorities_open = True
        st.session_state.side_by_side = False


def replace_product(index: int) -> None:
    """'Bytt produkt X': empty that field so the customer can type a new one."""
    st.session_state[input_key(index)] = ""
    st.session_state.products = None
    st.session_state.result = None
    st.session_state.side_by_side = False


def show_side_by_side() -> None:
    """'Vis likevel side om side'."""
    st.session_state.side_by_side = True


def compatibility():
    """Compatibility of the fetched products, or None before fetching."""
    from src.categories import detect_category
    from src.categories.compatibility import check
    products = st.session_state.get("products")
    return check([detect_category(p) for p in products]) if products else None


def weights(dimensions: list[str]) -> dict[str, int]:
    """Numeric weight per dimension from the chosen levels."""
    levels = st.session_state.levels
    return {dim: d.LEVELS[levels.get(dim, d.DEFAULT_LEVEL)] for dim in dimensions}
