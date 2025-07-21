import requests

from env import API_BASE


def authorized_get(url, token):
    return requests.get(f"{API_BASE}{url}", headers={"Authorization": f"Bearer {token}"})

def authorized_post(url, token, data=None):
    return requests.post(
        f"{API_BASE}{url}",
        headers={"Authorization": f"Bearer {token}"},
        json=data if data else {}
    )
