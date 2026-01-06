import requests
import os

BACKEND_BASE_URL = os.getenv("API_BASE_URL")
TIMEOUT = 10

def signup(email: str, password: str):
    res = requests.post(
        f"{BACKEND_BASE_URL}/auth/signup",
        json={
            "email": email,
            "password": password,
        },
        timeout=TIMEOUT,
    )

    if res.status_code == 200:
        return True

    raise ValueError(res.json().get("detail", "Signup failed"))

def confirm_signup(email: str, otp: str):
    res = requests.post(
        f"{BACKEND_BASE_URL}/auth/confirm-signup",
        json={
            "email": email,
            "otp": otp,
        },
        timeout=TIMEOUT,
    )

    if res.status_code == 200:
        return True

    raise ValueError(res.json().get("detail", "OTP verification failed"))

def login(email: str, password: str):
    print("Logging in with", email, password)
    res = requests.post(
        f"{BACKEND_BASE_URL}/auth/login",
        json={
            "email": email,
            "password": password,
        },
        timeout=TIMEOUT,
    )

    if res.status_code == 200:
        print("------", res.json())
        return res.json()

    raise ValueError(res.json().get("detail", "Login failed"))

def forgot_password(email: str):
    res = requests.post(
        f"{BACKEND_BASE_URL}/auth/forgot-password",
        json={"email": email},
        timeout=TIMEOUT,
    )

    if res.status_code == 200:
        return True

    raise ValueError(res.json().get("detail", "Failed to send OTP"))

def confirm_forgot_password(email: str, code: str, new_password: str):
    res = requests.post(
        f"{BACKEND_BASE_URL}/auth/confirm-forgot-password",
        json={
            "email": email,
            "code": code,
            "new_password": new_password,
        },
        timeout=TIMEOUT,
    )

    if res.status_code == 200:
        return True

    raise ValueError(res.json().get("detail", "Password reset failed"))
