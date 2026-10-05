import os
from flask import Flask, g
import psycopg
from psycopg.rows import dict_row


def get_db():
    if "db" not in g:
        url = os.environ.get("DATABASE_URL", "").strip()
        if not url:
            raise RuntimeError("DATABASE_URL is required")
        g.db = psycopg.connect(url, row_factory=dict_row)
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "schema.sql")) as f:
        db.execute(f.read())
    db.commit()


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "templates",
        ),
    )
    app.config.update(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "meta-local"),
        META_GRAPH_API_VERSION=os.environ.get("META_GRAPH_API_VERSION", "v24.0"),
        META_PAGE_ID=os.environ.get("META_PAGE_ID", "").strip(),
        META_ACCESS_TOKEN=os.environ.get("META_ACCESS_TOKEN", "").strip(),
        META_APP_ID=os.environ.get("META_APP_ID", "").strip(),
        META_APP_SECRET=os.environ.get("META_APP_SECRET", "").strip(),
        META_PUBLIC_URL=os.environ.get("META_PUBLIC_URL", "http://localhost:5004").rstrip("/"),
        LOCALS_ONLY_PUBLIC_URL=os.environ.get("LOCALS_ONLY_PUBLIC_URL", "http://localhost:5000").rstrip("/"),
    )
    app.teardown_appcontext(close_db)
    from .routes import bp
    app.register_blueprint(bp)
    with app.app_context():
        init_db()
    return app
