import streamlit as st


DEFAULT_SESSION_STATE = {
    # Auth
    "logged_in": False,
    "access_token": None,
    "id_token": None,

    # Profile
    "profile": None,
    "edit_mode": False,

    # Image upload
    "allow_image_upload": False,

    # Admin
    "show_admin_users": False,
    "admin_users": [],
    "admin_last_key": None,
    "admin_page": 0,

    # Signup
    "pending_email": None,
}


def init():
    """
    Initialize all session variables in one place.
    Safe to call multiple times.
    """
    for key, value in DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_tokens(access_token: str, id_token: str):
    st.session_state.logged_in = True
    st.session_state.access_token = access_token
    st.session_state.id_token = id_token


def reset_profile_state():
    st.session_state.profile = None
    st.session_state.edit_mode = False
    st.session_state.allow_image_upload = False


def reset_admin_state():
    st.session_state.admin_users = []
    st.session_state.admin_last_key = None
    st.session_state.admin_page = 0
    st.session_state.show_admin_users = False


def logout():
    """
    Full reset
    """
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]
