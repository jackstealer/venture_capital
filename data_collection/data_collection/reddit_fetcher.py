import os
import time
import requests
from requests.auth import HTTPBasicAuth

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"

def _get_token() -> str:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    if not client_id or not client_secret or not username or not password:
        print("Missing Reddit credentials, skipping Reddit fetch")
        return ""
    auth = HTTPBasicAuth(client_id, client_secret)
    data = {"grant_type": "password", "username": username, "password": password}
    headers = {"User-Agent": "VentureAlpha/0.1"}
    try:
        res = requests.post(TOKEN_URL, auth=auth, data=data, headers=headers)
        if res.status_code != 200:
            print(f"Reddit token fetch failed with status {res.status_code}")
            return ""
        payload = res.json() or {}
        token = payload.get("access_token", "")
        if not token:
            print("Reddit token missing in response")
        return token
    except Exception as e:
        print(f"Reddit token fetch failed: {e}")
        return ""

def fetch_reddit(subreddits: list, limit=25) -> list:
    token = _get_token()
    if not token:
        return []
    if not isinstance(subreddits, list):
        return []
    headers = {"Authorization": f"Bearer {token}", "User-Agent": "VentureAlpha/0.1"}
    all_posts = []
    for sub in subreddits:
        url = f"https://oauth.reddit.com/r/{str(sub)}/hot"
        params = {"limit": int(limit)}
        try:
            res = requests.get(url, headers=headers, params=params)
            if res.status_code != 200:
                print(f"Reddit fetch failed for r/{sub} with status {res.status_code}")
                continue
            data = res.json() or {}
            children = ((data.get("data") or {}).get("children")) or []
            for child in children:
                post = (child or {}).get("data") or {}
                if post:
                    all_posts.append(post)
        except Exception as e:
            print(f"Reddit fetch failed for r/{sub}: {e}")
        time.sleep(1)
    return all_posts

if __name__ == "__main__":
    default_subs = ["MachineLearning", "artificial", "singularity", "LocalLLaMA", "programming"]
    posts = fetch_reddit(default_subs)
    print(len(posts))

