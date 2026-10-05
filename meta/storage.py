import json
from . import get_db


def upsert_connection(user, meta_user_id, access_token, expires_at=None):
    db = get_db()
    row = db.execute(
        """INSERT INTO meta_connections
           (local_user_sub, local_user_email, local_user_name, local_user_picture,
            meta_user_id, access_token, expires_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s)
           ON CONFLICT (local_user_sub) DO UPDATE SET
             local_user_email=EXCLUDED.local_user_email,
             local_user_name=EXCLUDED.local_user_name,
             local_user_picture=EXCLUDED.local_user_picture,
             meta_user_id=EXCLUDED.meta_user_id,
             access_token=EXCLUDED.access_token,
             expires_at=EXCLUDED.expires_at,
             updated_at=CURRENT_TIMESTAMP
           RETURNING id""",
        (
            user["sub"], user.get("email", ""), user.get("name", ""),
            user.get("picture", ""), meta_user_id, access_token, expires_at,
        ),
    ).fetchone()
    db.commit()
    return row["id"]


def replace_pages(connection_id, pages):
    db = get_db()
    db.execute("DELETE FROM meta_pages WHERE connection_id=%s", (connection_id,))
    for page in pages:
        page_id = page.get("id")
        if not page_id:
            continue
        db.execute(
            """INSERT INTO meta_pages
               (connection_id, page_id, page_name, page_access_token, category, tasks, selected)
               VALUES (%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (page_id) DO UPDATE SET
                 connection_id=EXCLUDED.connection_id,
                 page_name=EXCLUDED.page_name,
                 page_access_token=EXCLUDED.page_access_token,
                 category=EXCLUDED.category,
                 tasks=EXCLUDED.tasks,
                 selected=EXCLUDED.selected""",
            (
                connection_id, page_id, page.get("name", ""),
                page.get("access_token", ""), page.get("category"),
                json.dumps(page.get("tasks", [])), True,
            ),
        )
    db.commit()


def get_connection(local_user_sub):
    db = get_db()
    return db.execute(
        "SELECT * FROM meta_connections WHERE local_user_sub=%s",
        (local_user_sub,),
    ).fetchone()


def get_pages(local_user_sub):
    db = get_db()
    return db.execute(
        """SELECT p.*
           FROM meta_pages p
           JOIN meta_connections c ON c.id=p.connection_id
           WHERE c.local_user_sub=%s
           ORDER BY p.page_name""",
        (local_user_sub,),
    ).fetchall()


def get_all_pages():
    db = get_db()
    return db.execute(
        """SELECT p.*, c.local_user_sub, c.local_user_email
           FROM meta_pages p
           JOIN meta_connections c ON c.id=p.connection_id
           WHERE p.page_access_token IS NOT NULL
             AND p.page_access_token <> ''
           ORDER BY p.id"""
    ).fetchall()


def delete_connection(local_user_sub):
    db = get_db()
    db.execute("DELETE FROM meta_connections WHERE local_user_sub=%s", (local_user_sub,))
    db.commit()


def store_posts(posts, page_id=None):
    db = get_db()
    inserted = 0
    for post in posts:
        post_id = post.get("id")
        if not post_id:
            continue
        cur = db.execute(
            """INSERT INTO meta_posts
              (facebook_id,page_id,message,created_time,permalink_url,image_url,raw_json)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (facebook_id) DO UPDATE SET
              page_id=EXCLUDED.page_id, message=EXCLUDED.message,
              created_time=EXCLUDED.created_time,
              permalink_url=EXCLUDED.permalink_url, image_url=EXCLUDED.image_url,
              raw_json=EXCLUDED.raw_json, fetched_at=CURRENT_TIMESTAMP
            RETURNING (xmax = 0) AS inserted""",
            (
                post_id, page_id, post.get("message", ""),
                post.get("created_time"), post.get("permalink_url"),
                post.get("full_picture"), json.dumps(post),
            ),
        )
        row = cur.fetchone()
        inserted += int(bool(row and row["inserted"]))
    db.commit()
    return inserted
