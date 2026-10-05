import requests
from flask import current_app


def graph_get(path, params=None, access_token=None):
    version = current_app.config["META_GRAPH_API_VERSION"].strip("/")
    token = access_token or current_app.config["META_ACCESS_TOKEN"]
    if not token:
        raise RuntimeError("No Meta access token is available")
    url = f"https://graph.facebook.com/{version}/{path.lstrip('/')}"
    query = dict(params or {})
    query["access_token"] = token
    response = requests.get(url, params=query, timeout=20)
    response.raise_for_status()
    return response.json()


def exchange_code(code, redirect_uri):
    version = current_app.config["META_GRAPH_API_VERSION"].strip("/")
    response = requests.get(
        f"https://graph.facebook.com/{version}/oauth/access_token",
        params={
            "client_id": current_app.config["META_APP_ID"],
            "client_secret": current_app.config["META_APP_SECRET"],
            "redirect_uri": redirect_uri,
            "code": code,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def get_meta_user(access_token):
    return graph_get("me", {"fields": "id,name,email"}, access_token=access_token)


def get_user_pages(access_token):
    return graph_get(
        "me/accounts",
        {"fields": "id,name,access_token,category,tasks", "limit": 100},
        access_token=access_token,
    ).get("data", [])


def get_page(page_id=None, access_token=None):
    page_id = page_id or current_app.config["META_PAGE_ID"]
    if not page_id:
        raise RuntimeError("No Meta Page is configured")
    return graph_get(
        page_id,
        {"fields": "id,name,about,link,picture{url}"},
        access_token=access_token,
    )


def get_page_posts(page_id=None, access_token=None, limit=25):
    page_id = page_id or current_app.config["META_PAGE_ID"]
    if not page_id:
        raise RuntimeError("No Meta Page is configured")
    return graph_get(
        f"{page_id}/posts",
        {"fields": "id,message,created_time,permalink_url,full_picture", "limit": limit},
        access_token=access_token,
    ).get("data", [])
