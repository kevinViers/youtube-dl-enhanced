'''
Version 1!!

First, checks downloadlist.txt for URLs to download. If none exist, it opens up terminal, prompts for URL

Sorts videos into folders first based on website domain then by MONTHYY date downloaded. 

--customfolder CUSTOMFOLDER after the url to save to a custom folder. Should(?) work with \ or / in the name but i haven't tested. I also think this will be linux only because of \ vs / which i learned last night 

Requires no additional files other than youtube-dl to be located in the same folder as the script. I should have made it try to call it systemwide if it's not in the same folder but too bad.    
'''

import subprocess
import platform
from datetime import datetime
import os

def download_video(url, custom_folder=None):
    MONTHYYtimestamp = datetime.now().strftime('%b%y').upper()
    
    if custom_folder:
        output_template = f"./{custom_folder}/{MONTHYYtimestamp}/%(playlist_title)s/%(title)s.%(ext)s"                                                      #save to custom folder
    else:
        output_template = f"./%(extractor)s/{MONTHYYtimestamp}/%(playlist_title)s/%(title)s.%(ext)s"                                                        #save to default folder
    
    os_name = platform.system()

    if custom_folder and not os.path.exists(custom_folder):                                                                                                 #create new folder on filesystem in case user's customfolder does not exist
        os.makedirs(custom_folder)

    if url:                                                                                                                                                 #URL exists
        if os_name == "Windows":
            result = subprocess.call(["cmd.exe", "/c", "youtube-dl.exe", "--output", output_template, url])                                                 #handling of different OS terminals. Only windows is tested
        elif os_name == "Darwin":  # steve jobs moment
            cmd = f'tell app "Terminal" to do script "youtube-dl.exe --output {output_template} {url}"'
            result = subprocess.call(["osascript", "-e", cmd])
        elif os_name == "Linux":
            result = subprocess.call(["gnome-terminal", "--", "youtube-dl.exe", "--output", output_template, url])
        else:
            print(f"whyare you data hoarding on a chromebook: {os_name}")
            return False

        return result == 0
    return False

if __name__ == "__main__":
    retry_counts = {}
    urls = []

    if os.path.exists("downloadlist.txt"):                                                                                                                  #downloadlist.txt exists, opening to read
        with open("downloadlist.txt", "r") as file:
            urls = [(url.strip(), None) for url in file.readlines()]                                                                                        #loop thru file, perform download on each one

    if not urls:                                                                                                                                            #URL not found in downloadlist, prompting for URL
        user_input = input("Enter the URL of the video you want to download (and optionally '-customfolder FOLDERNAME' to specify a custom folder): ")      #prompt for input
        tokens = user_input.split('-customfolder')                                                                                                          #custom folder handling
        url = tokens[0].strip()
        custom_folder = tokens[1].strip() if len(tokens) > 1 else None
        if url:                                                                                                                                             #add URL to urls list (not downloadlist.txt) to download
            urls.append((url, custom_folder))
    
    while urls:                                                                                                                                             #actual odwnloading part
        for url, custom_folder in urls:                                                                                                                     
            success = download_video(url, custom_folder)                                                                                                    #youtube-dl completes
            if not success:                                                                                                                                 
                retry_counts[url] = retry_counts.get(url, 0) + 1                                                                                            #retry downloading up to 3 times
                if retry_counts[url] > 3:
                    urls.remove((url, custom_folder))                                                                                                       #probably not worth downloading anyway
                    del retry_counts[url]                                                                                                                   #reset download attempt var
            else:
                urls.remove((url, custom_folder))
                if url in retry_counts:
                    del retry_counts[url]

        with open("downloadlist.txt", "w") as file:
            for remaining_url, _ in urls:
                file.write(remaining_url + "\n")

        if not urls:
            break
