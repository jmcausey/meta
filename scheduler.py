import os
import time
from meta import create_app
from meta.graph import get_page_posts
from meta.storage import store_posts

INTERVAL = int(os.environ.get("META_INTERVAL_SECONDS", "900"))
app = create_app()

with app.app_context():
    while True:
        try:
            posts = get_page_posts(50)
            print(f"Meta scheduler: fetched {len(posts)} posts, inserted {store_posts(posts)} new posts.", flush=True)
        except Exception as exc:
            print(f"Meta scheduler error: {exc}", flush=True)
        time.sleep(INTERVAL)
