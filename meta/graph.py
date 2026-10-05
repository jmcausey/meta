import requests
from flask import current_app

def graph_get(path, params=None):
    version = current_app.config["META_GRAPH_API_VERSION"].strip("/")
    url = f"https://graph.facebook.com/{version}/{path.lstrip('/')}"
    query = dict(params or {})
    query["access_token"] = current_app.config["META_ACCESS_TOKEN"]
    response = requests.get(url, params=query, timeout=20)
    response.raise_for_status()
    return response.json()

def get_page():
    page_id = current_app.config["META_PAGE_ID"]
    if not page_id:
        raise RuntimeError("META_PAGE_ID is not configured")
    return graph_get(page_id, {"fields": "id,name,about,link,picture{url}"})

def get_page_posts(limit=25):
    page_id = current_app.config["META_PAGE_ID"]
    if not page_id:
        raise RuntimeError("META_PAGE_ID is not configured")
    return graph_get(f"{page_id}/posts",
        {"fields": "id,message,created_time,permalink_url,full_picture", "limit": limit}
    ).get("data", [])
