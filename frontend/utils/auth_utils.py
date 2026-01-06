import jwt
import streamlit as st


def is_admin_user():
    token = jwt.decode(
        st.session_state.id_token,
        options={"verify_signature": False}
    )
    return "admin" in token.get("cognito:groups", [])
