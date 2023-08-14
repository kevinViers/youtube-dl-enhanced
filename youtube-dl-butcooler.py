'''
Version 2!

Basically V1 but with the following: 

* Integration with autosortv1.py
    Downloads videos into folders as the same as the old one did, however it also logs it in two locations two different ways-
        1. download_log.txt (should) store the following information
            Download date
            file size (broken)
            url
            average speed (broken)
            file name
            download location

        2. downloaded files stores the filename and the location on disk. This file gets manipulated by the autosorter.
* No comments
'''

import subprocess
import platform
from datetime import datetime
import os
import json
from urllib.parse import urlparse
import re

def get_domain_name(url):
    try:
        domain = urlparse(url).netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return "Unknown"

def sanitize_filename(title):
    words = re.findall(r'\b\w+\b', title)
    sanitized_title = "_".join(words).lower()
    return sanitized_title

def download_video(url, custom_folder=None):
    directory = "./"
    current_month_year = datetime.now().strftime('%b%y').upper()
    website_name = get_domain_name(url)

    if custom_folder:
        output_path = f"./{custom_folder}/{current_month_year}/%(title)s.%(ext)s"
    else:
        output_path = f"./{website_name}/{current_month_year}/%(title)s.%(ext)s"
        
    download_cmd = ["youtube-dl.exe", "--output", output_path, url]
    subprocess.run(download_cmd)

    metadata_cmd = ["youtube-dl.exe", "--output", output_path, "--print-json", "--skip-download", url]
    result = subprocess.run(metadata_cmd, capture_output=True, text=True)
    
    try:
        data = json.loads(result.stdout)
        file_title = sanitize_filename(data.get("title", "Unknown"))
        file_extension = data["_filename"].split(".")[-1]  # This fetches the file extension from the filename
        file_path = os.path.join(directory, website_name, current_month_year, f"{file_title}.{file_extension}")
        
        with open(file_path, "a") as f:
            f.write(f"\n\nURL: {url}")

        download_log = {
            "download_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "file_size": data.get("filesize", "Unknown"),
            "url": url,
            "avg_speed": data.get("download_speed", "Unknown"),
            "file_name": file_title,
            "download_location": os.path.dirname(file_path)
        }

        with open("download_log.txt", "a") as f:
            for key, value in download_log.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

        with open("downloaded_files.txt", "a") as f:
            f.write(f"{file_title},{os.path.dirname(file_path)}\n")

        return True

    except json.JSONDecodeError:
        print("Error decoding youtube-dl's JSON output.")
        return False



if __name__ == "__main__":
    retry_counts = {}
    urls = []

    if os.path.exists("downloadlist.txt"):
        with open("downloadlist.txt", "r") as file:
            for line in file:
                tokens = line.strip().split('-customfolder')
                url = tokens[0].strip()
                custom_folder = tokens[1].strip() if len(tokens) > 1 else None
                urls.append((url, custom_folder))

    if not urls:
        user_input = input("Enter the URL of the video you want to download (and optionally '-customfolder FOLDERNAME' to specify a custom folder): ")
        tokens = user_input.split('-customfolder')
        url = tokens[0].strip()
        custom_folder = tokens[1].strip() if len(tokens) > 1 else None
        urls.append((url, custom_folder))

    while urls:
        for url, custom_folder in urls:
            success = download_video(url, custom_folder)
            
            if not success:
                retry_counts[url] = retry_counts.get(url, 0) + 1
                if retry_counts[url] > 3:
                    print(f"Failed to download {url} after 3 attempts. Skipping.")
                    urls.remove((url, custom_folder))
                    del retry_counts[url]
            else:
                urls.remove((url, custom_folder))
                if url in retry_counts:
                    del retry_counts[url]

        with open("downloadlist.txt", "w") as file:
            for remaining_url, _ in urls:
                file.write(remaining_url + "\n")

        if not urls:
            break
