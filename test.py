import json

with open('tiktok_db.data1.json') as f:
    data = json.load(f)
data_lists=[]
for item in data:
    data_lists.append({
        "search_value": item["search_value"],
        "author_username": item["author_username"],
        "username": item["username"],
        "follower_count": item["follower_count"],
        "like_count": item["like_count"],
        "following_count": item["following_count"],
        "videoCount": item["author_details_info"]["videoCount"],
        "video_url": item["video_url"],
        "video_caption": item["video_caption"],
        "video_playCount": item["video_details_info"]["playCount"],
        "video_share_count": item["share_count"],
        "video_commentCount": item["video_details_info"]["commentCount"],
    })
    