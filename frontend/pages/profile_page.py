from datetime import date
import streamlit as st
from api.profile_api import get_profile, update_profile
from api.s3_identity import get_presigned_image_url, upload_image


def load_profile():
    resp, err = get_profile(st.session_state.id_token)
    if err:
        st.error(err)
        return
    st.session_state.profile = resp


def profile_page():
    if st.session_state.profile is None:
        load_profile()

    profile = st.session_state.profile or {}

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
