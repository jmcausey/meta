from flask import Blueprint, current_app, jsonify, render_template
from .graph import get_page, get_page_posts
from .storage import store_posts

bp = Blueprint("meta", __name__)

@bp.route("/")
def index():
    try:
        page = get_page()
        posts = get_page_posts(25)
        error = None
    except Exception as exc:
        page, posts, error = {}, [], str(exc)
    return render_template("index.html", page=page, posts=posts, error=error)

@bp.route("/api/page")
def api_page():
    try:
        return jsonify(get_page())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502

@bp.route("/api/posts")
def api_posts():
    try:
        posts = get_page_posts(25)
        store_posts(posts)
        return jsonify(posts)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502

@bp.route("/health")
def health():
    return jsonify({"status": "ok", "page_id_configured": bool(current_app.config["META_PAGE_ID"]),
                    "token_configured": bool(current_app.config["META_ACCESS_TOKEN"])})

@bp.route("/control")
def control():
    return render_template("control.html", page_id=current_app.config["META_PAGE_ID"],
                           graph_version=current_app.config["META_GRAPH_API_VERSION"])
