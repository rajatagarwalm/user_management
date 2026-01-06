import streamlit as st
from session import init, logout
from pages.auth_page import auth_page
from pages.profile_page import profile_page
from pages.admin_page import admin_page
from utils.auth_utils import is_admin_user

init()

st.set_page_config(
    page_title="User Profile App",
    layout="wide"
)

if not st.session_state.logged_in:
    auth_page()
    st.stop()

profile_page()

if is_admin_user():
    admin_page()

if st.button("Logout"):
    logout()
    st.rerun()
