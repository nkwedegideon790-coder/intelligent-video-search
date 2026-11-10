import streamlit as st
from Frontend.home import render

st.set_page_config(
    page_title="Intelligent Video Search",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="auto",
)
render()