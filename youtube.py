import requests
from config import YOUTUBE_API_KEY, PLAYLIST_ID


def get_playlist_videos():
    url = "https://www.googleapis.com/youtube/v3/playlistItems"

    videos = []
    page_token = None

    while True:

        params = {
            "part": "snippet",
            "playlistId": PLAYLIST_ID,
            "maxResults": 50,
            "key": YOUTUBE_API_KEY,
        }

        if page_token:
            params["pageToken"] = page_token

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        for item in data.get("items", []):

            snippet = item["snippet"]

            thumbnails = snippet.get("thumbnails", {})

            thumbnail = ""

            if "high" in thumbnails:
                thumbnail = thumbnails["high"]["url"]
            elif "medium" in thumbnails:
                thumbnail = thumbnails["medium"]["url"]
            elif "default" in thumbnails:
                thumbnail = thumbnails["default"]["url"]

            video_id = snippet["resourceId"]["videoId"]

            videos.append({
                "video_id": video_id,
                "title": snippet["title"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": thumbnail,
                "published_at": snippet["publishedAt"]
            })

        page_token = data.get("nextPageToken")

        if not page_token:
            break

    return videos
def get_video_comments(video_id):
    """
    指定した動画のコメントを取得する
    """

    url = "https://www.googleapis.com/youtube/v3/commentThreads"

    comments = []
    page_token = None

    while True:

        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": 100,
            "textFormat": "plainText",
            "key": YOUTUBE_API_KEY,
        }

        if page_token:
            params["pageToken"] = page_token

        response = requests.get(url, params=params)

        # コメントが無効・存在しない動画
        if response.status_code != 200:
            break

        data = response.json()

        for item in data.get("items", []):

            snippet = item["snippet"]["topLevelComment"]["snippet"]

            comments.append({
                "comment_id": item["id"],
                "video_id": video_id,
                "author": snippet.get("authorDisplayName", ""),
                "text": snippet.get("textDisplay", ""),
                "published_at": snippet.get("publishedAt", ""),
                "updated_at": snippet.get("updatedAt", ""),
                "like_count": snippet.get("likeCount", 0),
            })

        page_token = data.get("nextPageToken")

        if not page_token:
            break

    return comments

if __name__ == "__main__":

    videos = get_playlist_videos()

    print(f"取得動画数：{len(videos)}本")

    for video in videos:
        print(video["title"])