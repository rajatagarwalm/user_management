import json
import os
import requests
from requests.exceptions import RequestException, Timeout

API_BASE_URL = os.getenv("API_BASE_URL")


def headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def create_profile(token, payload):
    try:
        res = requests.post(
            f"{API_BASE_URL}/profile/create",
            headers=headers(token),
            json=payload,
            timeout=10,
        )
        res.raise_for_status()
        return res.json(), None

    except Exception as e:
        print("create_profile error:", e)
        return None, "Failed to create profile"


def get_profile(token):
    try:
        res = requests.get(
            f"{API_BASE_URL}/profile",
            headers=headers(token),
            timeout=10,
        )
        res.raise_for_status()
        return res.json(), None

    except Timeout:
        print("get_profile timeout")
        return None, "Server is taking too long to respond."

    except RequestException as e:
        print("get_profile error:", e)
        return None, "Unable to fetch profile. Please try again later."


def update_profile(token, payload):
    try:
        res = requests.put(
            f"{API_BASE_URL}/profile",
            headers=headers(token),
            json=payload,
            timeout=10,
        )
        res.raise_for_status()
        return res.json(), None

    except Timeout:
        print("update_profile timeout")
        return None, "Update timed out. Please try again."

    except RequestException as e:
        print("update_profile error:", e)
        return None, "Failed to update profile."


def get_all_users(id_token, last_key=None):
    try:
        headers = {"Authorization": f"Bearer {id_token}"}

        params = {"limit": 5}
        if last_key:
            params["last_key"] = json.dumps(last_key)

        res = requests.get(
            f"{API_BASE_URL}/admin/users",
            headers=headers,
            params=params,
            timeout=10,
        )
        res.raise_for_status()

        data = res.json()
        return {
            "items": data.get("items", []),
            "last_evaluated_key": data.get("last_evaluated_key"),
        }, None

    except Timeout:
        print("get_all_users timeout")
        return None, "Server is not responding."

    except RequestException as e:
        print("get_all_users error:", e)
        return None, "Unable to load users list."
