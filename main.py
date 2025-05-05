import os
import requests
import time
import glob
import logging

# Set up logging
log_dir = "./log"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=f"{log_dir}/downloaded_files.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def get_api_key():
    """Retrieve API key from environment or file, or prompt the user."""
    api_key = os.getenv("API_KEY")
    api_key_file = "./api_key.txt"

    if not api_key:
        if os.path.exists(api_key_file):
            with open(api_key_file, "r") as file:
                api_key = file.read().strip()
        else:
            api_key = input("Enter your API key: ").strip()
            with open(api_key_file, "w") as file:
                file.write(api_key)

    if not api_key:
        print("Error: API key is required.")
        exit(1)

    return api_key

def clear_console():
    """Clear the console in a cross-platform way."""
    os.system("cls" if os.name == "nt" else "clear")

def fetch_posts(api_key, base_query):
    """Fetch posts from the API and return the data."""
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
    """Extract media information from posts."""
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

def download_media(api_key, media_items, output_dir="./out"):
    """Download media items to the specified directory."""
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
    """Fetch gallery items from the API."""
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

    # Fetch and process gallery
    gallery = fetch_gallery(api_key)
    gallery_items = [item for item in gallery if not glob.glob(f"./out/{item['id']}.*")]
    print(f"Found {len(gallery_items)} new gallery items.")
    time.sleep(2)

    download_media(api_key, gallery_items)

if __name__ == "__main__":
    main()
