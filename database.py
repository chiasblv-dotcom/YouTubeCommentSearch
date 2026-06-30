import sqlite3
from config import DATABASE


def create_database():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # 既存テーブルを削除（初回のみ）
    cur.execute("DROP TABLE IF EXISTS comments")
    cur.execute("DROP TABLE IF EXISTS videos")

    # 動画テーブル
    cur.execute("""
        CREATE TABLE videos (
            video_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            thumbnail TEXT NOT NULL,
            published_at TEXT
        )
    """)

    # コメントテーブル
    cur.execute("""
        CREATE TABLE comments (
            comment_id TEXT PRIMARY KEY,
            video_id TEXT NOT NULL,
            author TEXT,
            comment TEXT NOT NULL,
            published_at TEXT,
            FOREIGN KEY(video_id) REFERENCES videos(video_id)
        )
    """)

    conn.commit()
    conn.close()

    print("データベースを初期化しました。")


if __name__ == "__main__":
    create_database()