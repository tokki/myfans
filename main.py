import requests
import re
import shutil
import os
import math
import argparse

headers = {
    "accept": "application/json, text/plain, */*",
    "authorization": "",
    "google-ga-data": "event328",
    "if-none-match": "",
}

user = {}  #globle userinfo


def get_user_info(name):
    url = "https://api.myfans.jp/api/v2/users/show_by_username?username="
    url = url + name
    try:
        res = requests.get(url, headers=headers)
        obj = res.json()
        user["id"] = obj["id"]
        user["username"] = obj["username"]
        user["posts_count"] = obj["posts_count"]
        user["post_videos_count"] = obj["post_videos_count"]
        user["post_images_count"] = obj["post_images_count"]
        print("get user " + user["username"] + "........")
    except:
        print("config header first")
        print("pay for the account")
        print("check your internet")
        print("good luck~~~")


def mkdir():
    path = "download/" + user["username"] + "/images/"
    path2 = "download/" + user["username"] + "/videos/"
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(path2):
        os.makedirs(path2)
    print("make dir done~~~")


def get_posts():
    posts = []
    limit = 15
    total_page = 0
    url = "https://api.myfans.jp/api/v1/users/" + user[
        "id"] + "/posts?page=current_page&sort_key=publish_start_at&limit=" + str(
            limit)
    if user["posts_count"] <= limit:
        total_page = 1
    else:
        total_page = math.ceil(user["posts_count"] / limit)
    #total_page = 2  #TODO for test
    for page in range(1, total_page + 1):
        uu = url.replace("current_page", str(page))
        res = requests.get(uu, headers=headers)
        post_list = res.json()
        for obj in post_list:
            posts.append(obj["id"])
    print("get all posts ...")
    return posts


def download_image(url):
    #url = "https://myfans.jp/_next/image?url=thisimageurl&w=1080&q=75"
    filename = re.findall("([a-zA-z0-9-]+.\w+)$", url)[0]
    try:
        res = requests.get(url)
        with open("download/" + user["username"] + "/images/" + filename,
                  'wb') as f:
            f.write(res.content)
            print("image:" + filename + "done...")
    except:
        print("download image error")


def download_video(url, post_id):
    uu = url.replace(".m3u8",
                     "/480p.m3u8")  #TODO req again to better than 480p??
    url = url.replace(".m3u8", "")
    try:
        req = requests.get(uu)
        playlist = []
        for line in req.text.split('\n'):
            if "#" not in line and ".ts" in line:
                playlist.append(url + "/" + line)
        with open(
                "download/" + user["username"] + "/videos/" + post_id + ".mp4",
                "wb") as f:
            for u in playlist:
                print("download.... :" + u)
                r = requests.get(u, stream=True)
                for c in r.iter_content(chunk_size=1024 * 1024):
                    if c:
                        f.write(c)
            print("video " + post_id + ".mp4 done~~~")
    except:
        print("download video error")


def download_post(post_id):
    url = "https://api.myfans.jp/api/v1/posts/" + post_id
    res = requests.get(url, headers=headers)
    post = res.json()
    if not post["visible"]:
        print("pay for this account")
        return
    if post["kind"] == "image":
        for img in post["post_images"]:
            download_image(img["file_url"])
    if post["kind"] == "video":
        mp4 = post["mp4_video_url"]
        download_video(mp4, post_id)


def download_one_post(post_id):
    url = "https://api.myfans.jp/api/v1/posts/" + post_id
    res = requests.get(url, headers=headers)
    post = res.json()
    if not post["visible"]:
        print("pay for this account")
        return
    else:
        user["username"] = post["user"]["username"]
        mkdir()

    if post["kind"] == "image":
        for img in post["post_images"]:
            download_image(img["file_url"])
    if post["kind"] == "video":
        mp4 = post["mp4_video_url"]
        download_video(mp4, post_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name",
        help="get all images videos from name in url",
    )
    parser.add_argument(
        "--post",
        help="get one post",
    )
    args = parser.parse_args()
    if args.name:
        get_user_info(args.name)
        mkdir()
        posts = get_posts(user)
        for post in posts:
            download_post(post)
    if args.post:
        download_one_post(args.post)
