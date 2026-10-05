import json
from . import get_db

def store_posts(posts):
    db = get_db()
    inserted = 0
    for post in posts:
        post_id = post.get("id")
        if not post_id:
            continue
        cur = db.execute(
            """INSERT INTO meta_posts
              (facebook_id,message,created_time,permalink_url,image_url,raw_json)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (facebook_id) DO UPDATE SET
              message=EXCLUDED.message, created_time=EXCLUDED.created_time,
              permalink_url=EXCLUDED.permalink_url, image_url=EXCLUDED.image_url,
              raw_json=EXCLUDED.raw_json, fetched_at=CURRENT_TIMESTAMP
            RETURNING (xmax = 0) AS inserted""",
            (post_id, post.get("message",""), post.get("created_time"),
             post.get("permalink_url"), post.get("full_picture"), json.dumps(post)),
        )
        row = cur.fetchone()
        inserted += int(bool(row and row["inserted"]))
    db.commit()
    return inserted
