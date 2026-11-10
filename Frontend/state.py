from __future__ import annotations

import streamlit as st

PAGES: dict = {}


def go(name: str) -> None:
    st.switch_page(PAGES[name])