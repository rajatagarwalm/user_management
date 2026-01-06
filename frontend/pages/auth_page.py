import streamlit as st
from api.auth_api import (
    login,
    signup,
    confirm_signup,
    forgot_password,
    confirm_forgot_password,
)
from api.profile_api import create_profile, get_profile
from session import set_tokens


def load_profile():
    resp, err = get_profile(st.session_state.id_token)
    if err:
        st.error(err)
        return
    st.session_state.profile = resp


def auth_page():
    tabs = st.tabs(["Login", "Signup"])

    with tabs[0]:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login"):
                try:
                    auth = login(email, password)
                    set_tokens(auth["AccessToken"], auth["IdToken"])
                    load_profile()
                    st.session_state.edit_mode = False
                    st.session_state.show_admin_users = False
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        with col2:
            if st.button("Forgot Password?"):
                st.session_state.forgot_flow = True
                st.session_state.reset_email = email

    with tabs[1]:
        email = st.text_input(label="Signup Email")
        password = st.text_input("Signup Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        name = st.text_input("Name")
        height = st.text_input("Height")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        dob = st.date_input("Date of Birth")

        if st.button("Signup"):
            if password != confirm_password:
                st.error("Passwords do not match")
                st.stop()

            signup(email, password)

            st.session_state.pending_email = email
            st.session_state.pending_password = password
            st.session_state.pending_profile = {
                "name": name,
                "height": height,
                "gender": gender,
                "dob": dob.isoformat(),
            }

            st.success("OTP sent to your email")

        if st.session_state.pending_email:
            otp = st.text_input("Enter OTP")

            if st.button("Verify Email"):
                confirm_signup(st.session_state.pending_email, otp)
                auth = login(
                    st.session_state.pending_email,
                    st.session_state.pending_password,
                )

                set_tokens(auth["AccessToken"], auth["IdToken"])

                create_profile(
                    st.session_state.id_token,
                    st.session_state.pending_profile,
                )

                st.session_state.pending_email = None
                st.session_state.pending_password = None
                st.session_state.pending_profile = None

                st.success("Signup completed 🎉")
                st.rerun()

    if st.session_state.get("forgot_flow"):
        st.divider()
        st.subheader("Reset Password")

        email = st.text_input(
            "Email",
            value=st.session_state.get("reset_email", ""),
        )

        if not st.session_state.get("reset_code_sent"):
            if st.button("Send OTP"):
                forgot_password(email)
                st.session_state.reset_code_sent = True
                st.success("OTP sent")
                st.rerun()
        else:
            code = st.text_input("OTP")
            new_password = st.text_input("New Password", type="password")

            if st.button("Confirm Reset"):
                confirm_forgot_password(email, code, new_password)
                st.session_state.forgot_flow = False
                st.session_state.reset_code_sent = False
                st.success("Password reset successful")
                st.rerun()
