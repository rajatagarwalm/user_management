import streamlit as st
import jwt
from dotenv import load_dotenv
import pandas as pd
from datetime import date

load_dotenv()

from auth import confirm_signup, confirm_forgot_password, forgot_password, login, signup
from api import create_profile, get_profile, update_profile, get_all_users
from s3_identity import upload_image, get_presigned_image_url
from session import init, set_tokens, logout

init()

st.set_page_config(
    page_title="User Profile App",
    layout="wide"
)

def load_profile():
    resp, err = get_profile(st.session_state.id_token)
    if err:
        st.error(err)
        return
    st.session_state.profile = resp

if not st.session_state.logged_in:
    tabs = st.tabs(["Login", "Signup"])

    with tabs[0]:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login"):
                with st.spinner("Logging in..."):
                    try:
                        auth = login(email, password)

                        if not auth:
                            st.error("Invalid email or password")
                        else:
                            set_tokens(auth["AccessToken"], auth["IdToken"])
                            load_profile()
                            st.session_state.edit_mode = False
                            st.session_state.show_admin_users = False
                            st.rerun()

                    except ValueError as e:
                        st.error(str(e))

                    except RuntimeError as e:
                        st.error(str(e))

        with col2:
            if st.button("Forgot Password?"):
                st.session_state.forgot_flow = True
                st.session_state.reset_email = email

    with tabs[1]:
        st.subheader("Signup")

        email = st.text_input("email")
        password = st.text_input("password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        name = st.text_input("Name")
        height = st.text_input("Height")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        dob = st.date_input("Date of Birth")

        if st.button("Signup"):
            if password != confirm_password:
                st.error("Passwords do not match")
                st.stop()

            try:
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

            except ValueError as e:
                st.error(str(e))

            except RuntimeError:
                st.error("Signup service is unavailable")

        # ---------- OTP Verification ----------
        if st.session_state.pending_email:
            otp = st.text_input("Enter OTP")

            if st.button("Verify Email"):
                try:
                    confirm_signup(st.session_state.pending_email, otp)
                    auth = login(
                        st.session_state.pending_email,
                        st.session_state.pending_password,
                    )

                    if not auth:
                        st.error("Login failed after verification")
                        st.stop()

                    set_tokens(auth["AccessToken"], auth["IdToken"])

                    _, err = create_profile(
                        st.session_state.id_token,
                        st.session_state.pending_profile,
                    )

                    if err:
                        st.error(err)
                        st.stop()

                    st.session_state.pending_email = None
                    st.session_state.pending_password = None
                    st.session_state.pending_profile = None

                    st.success("Signup completed successfully 🎉")
                    st.rerun()

                except ValueError as e:
                    st.error(str(e))

                except RuntimeError:
                    st.error("Verification failed. Try again.")


    if st.session_state.get("forgot_flow"):
        st.divider()
        st.subheader("Reset Password")

        reset_email = st.text_input(
            "Email ID",
            value=st.session_state.get("reset_email", ""),
        )

        if not st.session_state.get("reset_code_sent"):
            if st.button("Send OTP"):
                with st.spinner("Sending OTP..."):
                    try:
                        forgot_password(reset_email)
                        st.session_state.reset_code_sent = True
                        st.success("OTP sent to your email")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

                    except RuntimeError as e:
                        st.error(str(e))

        else:
            code = st.text_input("Enter OTP")
            new_password = st.text_input(
                "New Password", type="password"
            )

            if st.button("Confirm Reset"):
                with st.spinner("Resetting password..."):
                    try:
                        confirm_forgot_password(
                            reset_email,
                            code,
                            new_password,
                        )
                        st.success("Password reset successful")
                        st.session_state.forgot_flow = False
                        st.session_state.reset_code_sent = False
                        st.rerun()

                    except ValueError as e:
                        st.error(str(e))

                    except RuntimeError as e:
                        st.error(str(e))

    st.stop()

if st.session_state.profile is None:
    load_profile()

profile = st.session_state.profile or {}

decoded_token = jwt.decode(
    st.session_state.id_token,
    options={"verify_signature": False}
)

is_admin = "admin" in decoded_token.get("cognito:groups", [])

col1, col2 = st.columns([1, 3])

with col1:
    try:
        image_url = get_presigned_image_url(st.session_state.id_token)
        image_exists = True
    except FileNotFoundError:
        image_url = "assets/avatar.jpg"
        image_exists = False
    except Exception:
        image_url = "assets/avatar.jpg"
        image_exists = False

    st.image(image_url, width=150)

    if image_exists and not st.session_state.allow_image_upload:
        if st.button("Replace Image"):
            st.session_state.allow_image_upload = True
            st.rerun()

    if not image_exists or st.session_state.allow_image_upload:
        st.markdown("### Upload Profile Image")

        img = st.file_uploader(
            "Choose image (Max 2 MB)",
            type=["jpg", "png"],
            key="profile_image"
        )

        if img:
            if img.size / (1024 * 1024) > 2:
                st.error("Image size must be 2 MB or less")
            else:
                if st.button("Upload Image"):
                    try:
                        upload_image(st.session_state.id_token, img)
                        st.session_state.allow_image_upload = False
                        st.success("Image uploaded successfully")
                        st.rerun()
                    except Exception:
                        st.error("Image upload failed. Please try again.")

with col2:
    st.markdown("### Profile Details")

    st.text_input(
        "Email",
        profile.get("email", ""),
        disabled=True
    )

    def field(label, key):
        return st.text_input(
            label,
            str(profile.get(key, "")),
            disabled=not st.session_state.edit_mode
        )

    name = field("Name", "name")
    height = field("Height", "height")
    gender = field("Gender", "gender")

    existing_dob = None
    if profile.get("dob"):
        try:
            existing_dob = date.fromisoformat(profile["dob"])
        except ValueError:
            existing_dob = None

    dob = st.date_input(
        "DOB",
        value=existing_dob,
        disabled=not st.session_state.edit_mode
    )

    if not st.session_state.edit_mode:
        if st.button("Edit Profile"):
            st.session_state.edit_mode = True
            st.rerun()
    else:
        colA, colB = st.columns(2)

        if colA.button("Save"):
            with st.spinner("Updating profile..."):
                _, err = update_profile(
                    st.session_state.id_token,
                    {
                        "name": name,
                        "height": height,
                        "gender": gender,
                        "dob": dob.isoformat() if dob else None,
                    }
                )

                if err:
                    st.error(err)
                else:
                    load_profile()
                    st.session_state.edit_mode = False
                    st.success("Profile updated successfully")
                    st.rerun()

        if colB.button("Cancel"):
            st.session_state.edit_mode = False
            st.rerun()

if is_admin:
    st.divider()
    st.subheader("Admin Panel")

    PAGE_SIZE = 5

    if st.button("List All Users"):
        with st.spinner("Fetching users..."):
            resp, err = get_all_users(st.session_state.id_token)
            if err:
                st.error(err)
            elif resp and resp["items"]:
                st.session_state.admin_users = resp["items"]
                st.session_state.admin_last_key = resp["last_evaluated_key"]
                st.session_state.admin_page = 0
            else:
                st.warning("No users found")

    if st.session_state.admin_users:
        start = st.session_state.admin_page * PAGE_SIZE
        end = start + PAGE_SIZE

        df = pd.DataFrame(st.session_state.admin_users[start:end])
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.session_state.admin_page > 0:
                if st.button("⬅ Previous"):
                    st.session_state.admin_page -= 1
                    st.rerun()

        with col2:
            if end < len(st.session_state.admin_users):
                if st.button("Next ➡"):
                    st.session_state.admin_page += 1
                    st.rerun()

st.divider()

if st.button("Logout"):
    logout()
    st.rerun()
