import json
import os
import requests
import time
import glob
import logging
import configparser
from dateutil.parser import isoparse

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")

LOG_DIR = config.get("Paths", "log_dir", fallback="./log")
OUT_DIR = config.get("Paths", "out_dir", fallback="./out")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_DIR}/downloaded_files.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def get_api_key():
    api_key = os.getenv("API_KEY")
    config_file = "config.ini"

    if not api_key:
        if config.has_option("Credentials", "api_key"):
            api_key = config.get("Credentials", "api_key")
        else:
            api_key = input("Enter your API key: ").strip()
            if not config.has_section("Credentials"):
                config.add_section("Credentials")
            config.set("Credentials", "api_key", api_key)
            with open(config_file, "w", encoding="utf-8") as file:
                config.write(file)

    if not api_key:
        print("Error: API key is required.")
        exit(1)

    return api_key

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

def fetch_posts(api_key, base_query):
    cursor = ""
    out_data = []
    iteration = 1
    total_posts = 0

    while True:
        clear_console()
        print(f"Fetching posts, Iteration {iteration}: {total_posts} posts so far.")
        full_query = base_query if not cursor else f"{base_query}&cursor={cursor}"
        response = requests.get(
            "https://api.parentzone.me/v1/posts",
            headers={"x-api-key": api_key},
            params=full_query,
        )

        if response.status_code == 200:
            parsed_response = response.json()
            posts = parsed_response.get("posts", [])
            out_data.extend(posts)
            total_posts += len(posts)
            cursor = parsed_response.get("cursor", "")
            if not posts:
                break
            time.sleep(0.5)  # Rate limit
        else:
            if response.status_code == 401:
                print("Error: API key is wrong or expired.")
            else:
                print(f"Error: {response.status_code} - {response.reason}")
            break

        iteration += 1

    return out_data

def process_media(posts):
    media_items = []
    for post in posts:
        if "media" in post:
            for media in post["media"]:
                media_items.append({
                    "id": media["id"],
                    "child": f"{post['child']['forename']} {post['child']['surname']}",
                    "timestamp": media["updated"],
                    "author": f"{post['author']['forename']} {post['author']['surname']}",
                })
    return media_items

def download_media(api_key, media_items, output_dir=OUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    for count, media in enumerate(media_items, start=1):
        media_id = media["id"]
        if not glob.glob(f"{output_dir}/{media_id}.*"):
            print(f"Downloading media {count} of {len(media_items)} id: {media_id}")
            url = f"https://api.parentzone.me/v1/media/{media_id}/full"
            response = requests.get(url, headers={"x-api-key": api_key})
            if response.status_code == 200:
                content_type = response.headers["Content-Type"]
                ext = content_type.split("/")[1]
                file_path = f"{output_dir}/{media_id}.{ext}"
                with open(file_path, "wb") as file:
                    file.write(response.content)
                logging.info(f"Downloaded: {file_path}")
            time.sleep(0.5)
        clear_console()

def fetch_gallery(api_key):
    response = requests.get(
        "https://api.parentzone.me/v1/gallery/",
        headers={"x-api-key": api_key},
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []

def save_metadata(media_items, metadata_file=f"{OUT_DIR}/metadata.json"):
    os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
    with open(metadata_file, "w", encoding="utf-8") as file:
        json.dump(media_items, file, indent=4)
    logging.info(f"Metadata saved to: {metadata_file}")

def process_metadata(metadata_file_path, timestamp_key):
    print(f"Processing metadata file: {metadata_file_path} with timestamp key: {timestamp_key}")
    with open(metadata_file_path, "r") as file:
        metadata = json.load(file)

    for item in metadata:
        file_id = item.get("id")
        if not file_id:
            print("Skipping item with missing 'id'")
            continue

        jpeg_path = os.path.join("out", f"{file_id}.jpeg")
        mp4_path = os.path.join("out", f"{file_id}.mp4")

        for path in [jpeg_path, mp4_path]:
            if os.path.isfile(path):
                timestamp = item.get(timestamp_key)
                if timestamp:
                    ts = int(isoparse(timestamp).timestamp())
                    os.utime(path, (ts, ts))
                    print(f"Updated timestamp for {path} to {ts}")
                break
            else:
                print(f"File not found: {path}")

def main():
    api_key = get_api_key()
    base_query = "typeIDs[]=14&typeIDs[]=12"

    # Fetch and process posts
    posts = fetch_posts(api_key, base_query)
    media_items = process_media(posts)
    print(f"Found {len(media_items)} media items.")
    time.sleep(2)

    # Download media items
    download_media(api_key, media_items)

    # Save metadata
    save_metadata(media_items, metadata_file=f"{OUT_DIR}/posts_metadata.json")

    # Fetch and process gallery
    gallery = fetch_gallery(api_key)
    save_metadata(gallery, metadata_file=f"{OUT_DIR}/gallery_metadata.json")
    gallery_items = [item for item in gallery if not glob.glob(f"{OUT_DIR}/{item['id']}.*")]
    print(f"Found {len(gallery_items)} new gallery items.")
    time.sleep(2)

    download_media(api_key, gallery_items)

    # Process metadata files
    process_metadata(os.path.join(OUT_DIR, "posts_metadata.json"), "timestamp")
    process_metadata(os.path.join(OUT_DIR, "gallery_metadata.json"), "updated")

if __name__ == "__main__":
    main()
