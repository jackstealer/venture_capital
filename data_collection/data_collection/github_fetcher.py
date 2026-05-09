import os
import time
import requests
import urllib.parse as urlparse

def fetch_github(queries: list, max_per_query=10) -> list:
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"} if token else {"Accept": "application/vnd.github.v3+json"}
    url = "https://api.github.com/search/repositories"
    all_results = []
    if not isinstance(queries, list):
        return []
    for query in queries:
        params = {"q": str(query), "sort": "stars", "order": "desc", "per_page": int(max_per_query)}
        print(f"Fetching GitHub repos for query: {query}")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            items = response.json().get("items", [])
        except Exception as e:
            print(f"GitHub fetch failed for query '{query}': {e}")
            continue
        for item in items[:int(max_per_query)]:
            owner = item.get("owner", {}).get("login", "")
            repo = item.get("name", "")
            contributors = 0
            if owner and repo:
                contrib_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
                contrib_params = {"per_page": 1, "anon": "true"}
                try:
                    c_res = requests.get(contrib_url, headers=headers, params=contrib_params)
                    if c_res.status_code == 200:
                        link = c_res.headers.get("Link", "")
                        if 'rel="last"' in link:
                            parts = link.split(",")
                            for p in parts:
                                if 'rel="last"' in p:
                                    url_part = p.split(";")[0].strip("<> ")
                                    parsed = urlparse.urlparse(url_part)
                                    qs = urlparse.parse_qs(parsed.query)
                                    if "page" in qs:
                                        try:
                                            contributors = int(qs["page"][0])
                                        except Exception:
                                            contributors = 0
                        else:
                            try:
                                contributors = len(c_res.json())
                            except Exception:
                                contributors = 0
                    time.sleep(1)
                except Exception as e:
                    print(f"Contributors fetch failed for {repo}: {e}")
            result = {
                "name": item.get("name", "") or "",
                "description": item.get("description", "") or "",
                "html_url": item.get("html_url", "") or "",
                "stargazers_count": int(item.get("stargazers_count", 0) or 0),
                "contributor_count": int(contributors or 0),
                "owner_login": owner or "",
                "created_at": item.get("created_at", "") or "",
                "topics": item.get("topics", []) or [],
            }
            all_results.append(result)
    return all_results

if __name__ == "__main__":
    sample = fetch_github(["AI agents"])
    print(len(sample))
