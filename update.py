import sqlite3
import time
from requests.exceptions import RequestException

from config import DATABASE
from youtube import (
    get_playlist_videos,
    get_video_comments,
)


def save_video(cur, video):
    """
    動画情報を追加・更新する
    """

    cur.execute(
        """
        SELECT
            title,
            url,
            thumbnail,
            published_at
        FROM videos
        WHERE video_id = ?
        """,
        (video["video_id"],),
    )

    row = cur.fetchone()

    if row is None:

        cur.execute(
            """
            INSERT INTO videos
            (
                video_id,
                title,
                url,
                thumbnail,
                published_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                video["video_id"],
                video["title"],
                video["url"],
                video["thumbnail"],
                video["published_at"],
            ),
        )

        return "insert"

    if (
        row[0] != video["title"]
        or row[1] != video["url"]
        or row[2] != video["thumbnail"]
        or row[3] != video["published_at"]
    ):

        cur.execute(
            """
            UPDATE videos
            SET
                title = ?,
                url = ?,
                thumbnail = ?,
                published_at = ?
            WHERE video_id = ?
            """,
            (
                video["title"],
                video["url"],
                video["thumbnail"],
                video["published_at"],
                video["video_id"],
            ),
        )

        return "update"

    return "skip"


def save_comment(cur, comment):
    """
    コメントを保存する
    """

    cur.execute(
        """
        INSERT OR REPLACE INTO comments
        (
            comment_id,
            video_id,
            author,
            comment,
            published_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            comment["comment_id"],
            comment["video_id"],
            comment["author"],
            comment["text"],
            comment["published_at"],
        ),
    )


def main():

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    print("=" * 70)
    print("YouTubeデータ更新開始")
    print("=" * 70)

    print()
    print("動画一覧取得中...")

    videos = get_playlist_videos()

    total_videos = len(videos)

    print(f"{total_videos}件取得しました。")
    print()

    new_videos = 0
    updated_videos = 0
    total_comments = 0

    for index, video in enumerate(videos, start=1):

        print("=" * 70)
        print(f"[{index}/{total_videos}]")
        print(video["title"])

        result = save_video(cur, video)

        if result == "insert":
            new_videos += 1
            print("動画：新規追加")

        elif result == "update":
            updated_videos += 1
            print("動画：更新")

        else:
            print("動画：変更なし")

        print("コメント取得中...")

        try:

            comments = get_video_comments(video["video_id"])

        except RequestException as e:

            print("コメント取得失敗")
            print(e)
            print()

            continue

        except Exception as e:

            print("予期しないエラー")
            print(e)
            print()

            continue

        print(f"{len(comments)}件取得")

        saved_comments = 0

        for comment in comments:

            try:

                save_comment(cur, comment)
                saved_comments += 1

            except sqlite3.Error as e:

                print("コメント保存エラー")
                print(e)

        total_comments += saved_comments

        print(f"{saved_comments}件保存")

        conn.commit()

        # API制限対策
        time.sleep(0.2)

    print()
    print("=" * 70)
    print("データベース集計中...")
    print("=" * 70)

    cur.execute(
        """
        SELECT COUNT(*)
        FROM videos
        """
    )

    db_videos = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM comments
        """
    )

    db_comments = cur.fetchone()[0]

    conn.commit()
    conn.close()

    print()
    print("=" * 70)
    print("更新完了")
    print("=" * 70)

    print(f"取得動画数       : {total_videos}")
    print(f"新規動画         : {new_videos}")
    print(f"更新動画         : {updated_videos}")
    print(f"今回保存コメント : {total_comments}")
    print(f"DB動画数         : {db_videos}")
    print(f"DBコメント数     : {db_comments}")

    print("=" * 70)


if __name__ == "__main__":
    main()

osusu