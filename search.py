import sqlite3

from config import DATABASE


def search_comments(keyword):

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        """
        SELECT DISTINCT
            videos.title,
            videos.url,
            videos.published_at
        FROM comments
        JOIN videos
            ON comments.video_id = videos.video_id
        WHERE comments.comment LIKE ?
        ORDER BY videos.published_at DESC
        """,
        (f"%{keyword}%",)
    )

    results = cur.fetchall()

    conn.close()

    return results


def main():

    print("=" * 60)
    print("YouTubeコメント検索")
    print("=" * 60)

    while True:

        keyword = input("\n検索キーワード（終了:q）> ").strip()

        if keyword.lower() == "q":
            break

        if keyword == "":
            continue

        results = search_comments(keyword)

        print()
        print("=" * 60)
        print(f"検索結果：{len(results)}件")
        print("=" * 60)

        if not results:
            print("該当する動画はありません。")
            continue

        for i, row in enumerate(results, start=1):

            published = row["published_at"]

            # 2024-06-01T12:34:56Z → 2024-06-01
            if published:
                published = published[:10]

            print(f"{i}. {row['title']}")
            print(f"   投稿日 : {published}")
            print(f"   URL     : {row['url']}")
            print()

    print("\n終了しました。")


if __name__ == "__main__":
    main()