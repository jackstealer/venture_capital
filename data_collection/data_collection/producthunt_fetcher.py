import os
import requests

GRAPHQL_ENDPOINT = "https://api.producthunt.com/v2/api/graphql"

def fetch_producthunt(max_results=20) -> list:
    token = os.getenv("PRODUCTHUNT_TOKEN")
    if not token:
        print("Missing PRODUCTHUNT_TOKEN, skipping Product Hunt fetch")
        return []
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    limit = int(max_results) if max_results else 20
    query = """
    query {
      posts(order: VOTES, first: %d) {
        edges {
          node {
            name
            tagline
            votesCount
            commentsCount
            createdAt
            website
            topics {
              edges {
                node { name }
              }
            }
          }
        }
      }
    }
    """ % limit
    try:
        res = requests.post(GRAPHQL_ENDPOINT, headers=headers, json={"query": query})
        res.raise_for_status()
        data = res.json()
        edges = (((data or {}).get("data") or {}).get("posts") or {}).get("edges", [])
        nodes = []
        for edge in edges:
            node = (edge or {}).get("node") or {}
            if node:
                nodes.append(node)
        return nodes
    except Exception as e:
        print(f"Product Hunt fetch failed: {e}")
        return []

if __name__ == "__main__":
    items = fetch_producthunt()
    print(len(items))

