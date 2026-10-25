"""The row of product-group tabs at the top (MDA, SDA, Data, Gaming, Mobil, TV og lyd).

The open tab decides which product types a varekode is matched against,
so a stick vacuum searched under SDA is always read as a vacuum.
"""
from __future__ import annotations

from html import escape

import streamlit as st

from src.categories.groups import BY_ID, GROUPS
from src.ui import state
from src.ui.components import html


def current():
    """The open tab (Group)."""
    return BY_ID[st.session_state.get("group", state.DEFAULT_GROUP)]


def render() -> None:
    """Draw the tab row and a one-line hint for the open tab."""
    active = current()
    with st.container(key="group_tabs"):
        columns = st.columns(len(GROUPS), gap="small")
        for column, group in zip(columns, GROUPS):
            with column:
                st.button(group.name, key=f"group_{group.id}", width="stretch",
                          type="primary" if group.id == active.id else "secondary",
                          on_click=state.set_group, args=(group.id,), disabled=group.id == active.id)
    html(f'<div class="ps-group-hint">{escape(active.hint)}</div>')
