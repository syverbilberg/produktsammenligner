"""Session state: what has been fetched and decided so far.

Flow: inputs → fetched products → priorities → result. Changing an input
after fetching clears everything downstream. Each product-group tab (MDA,
Mobil …) keeps its own copy, see set_group.
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


def _group() -> str:
    return st.session_state.get("group", DEFAULT_GROUP)


def input_key(index: int, group: str | None = None) -> str:
    """Widget key for product field `index` (0-based) in a tab.

    Every tab has its own fields ("input_mobile_0"). Sharing one set of fields
    and refilling them does not work: the browser keeps what was typed and
    sends it back, so MDA's varekoder ended up in Mobil's fields.
    """
    return f"input_{group or _group()}_{index}"


def _typed(group: str | None = None) -> dict[int, str]:
    """What has been typed in a tab, kept outside the widgets.

    Streamlit forgets a widget's value when it is not on screen (another tab
    is open), so the text is copied here and put back when the tab opens.
    """
    return st.session_state.setdefault("typed", {}).setdefault(group or _group(), {})


def init() -> None:
    """Create missing keys with defaults."""
    for key, value in _DEFAULTS.items():
        st.session_state.setdefault(key, value.copy() if isinstance(value, (list, dict)) else value)
    st.session_state.setdefault("group", DEFAULT_GROUP)


def restore_inputs() -> None:
    """Put the open tab's typed text back into its fields (before they are drawn)."""
    for index, value in _typed().items():
        if index < st.session_state.count and input_key(index) not in st.session_state:
            st.session_state[input_key(index)] = value


def remember_inputs() -> None:
    """Copy what is in the open tab's fields to the per-tab store."""
    typed = _typed()
    for index in range(st.session_state.count):
        if input_key(index) in st.session_state:
            typed[index] = st.session_state[input_key(index)]


def set_group(group_id: str, keep_inputs: bool = False) -> None:
    """Open another tab.

    Each tab keeps its own comparison: what was typed, fetched and chosen in
    MDA is still there after looking at Mobil. `keep_inputs` is for
    "Bytt til fanen …": the typed varekoder move to the new tab and the old
    tab starts empty, since they did not belong there.
    """
    current = _group()
    if group_id == current:
        return
    remember_inputs()
    store = st.session_state.setdefault("saved_groups", {})
    if keep_inputs:
        moved, count = dict(_typed(current)), st.session_state.count
        reset()                                   # empties the old tab
        st.session_state.group = group_id
        _typed().clear()
        _typed().update(moved)
        st.session_state.count = count
        for index in range(MAX_PRODUCTS):          # the new tab's fields must show the moved text
            st.session_state.pop(input_key(index), None)
        return
    store[current] = {key: st.session_state.get(key) for key in _DEFAULTS}
    target = store.pop(group_id, {})
    for key, value in _DEFAULTS.items():
        st.session_state[key] = value.copy() if isinstance(value, (list, dict)) else value
    for key in [k for k in st.session_state if str(k).startswith("level_")]:
        del st.session_state[key]
    st.session_state.group = group_id
    for key, value in target.items():
        st.session_state[key] = value


def reset() -> None:
    """Start a new comparison in the open tab ("↺ Ny"). Other tabs are kept."""
    for key, value in _DEFAULTS.items():
        st.session_state[key] = value.copy() if isinstance(value, (list, dict)) else value
    for index in range(MAX_PRODUCTS):
        if input_key(index) in st.session_state:
            st.session_state[input_key(index)] = ""      # set, not delete: the browser would send the old text back
    _typed().clear()
    for key in [k for k in st.session_state if str(k).startswith("level_")]:
        del st.session_state[key]


def add_product() -> None:
    """Show one more product field (max 4)."""
    st.session_state.count = min(st.session_state.count + 1, MAX_PRODUCTS)


def remove_product(index: int) -> None:
    """Remove field `index` and shift the ones below it up."""
    remember_inputs()
    count = st.session_state.count
    typed = _typed()
    for i in range(index, count - 1):
        value = st.session_state.get(input_key(i + 1), "")
        st.session_state[input_key(i)] = value
        typed[i] = value
    st.session_state[input_key(count - 1)] = ""
    typed.pop(count - 1, None)
    st.session_state.count = max(count - 1, MIN_PRODUCTS)


def current_inputs() -> tuple[str, ...]:
    """What is typed in the open tab's product fields right now."""
    typed = _typed()
    return tuple(str(st.session_state.get(input_key(i), typed.get(i, ""))).strip() for i in range(st.session_state.count))


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
    _typed()[index] = ""
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
