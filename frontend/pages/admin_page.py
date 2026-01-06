import streamlit as st
import pandas as pd
from api.profile_api import get_all_users


def admin_page():
    st.divider()
    st.subheader("Admin Panel")

    if st.button("List All Users"):
        resp, _ = get_all_users(st.session_state.id_token)
        st.session_state.admin_users = resp["items"]

    if st.session_state.get("admin_users"):
        df = pd.DataFrame(st.session_state.admin_users)
        st.dataframe(df, use_container_width=True)
