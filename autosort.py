import os
from difflib import SequenceMatcher
from collections import deque

required_similarity = 0.25 #required length (as a percent) of a substring from video A must be present in video B for a match

def longest_common_substring(s1, s2):
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]

def similarity(a, b):
    lcs = longest_common_substring(a, b)
    return len(lcs) / len(a) 


def bfs_folder_search(directory, filename):
    queue = deque([directory])
    while queue:
        current_dir = queue.popleft()
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            if os.path.isdir(item_path):
                if item in filename:
                    return item_path
                queue.append(item_path)
    return None

def move_files_based_on_similarity(directory, all_files_list):
    for file1 in all_files_list:
        similar_files = [file1]
        for file2 in all_files_list:
            if file1 != file2:
                sim = similarity(os.path.basename(file1), os.path.basename(file2))
                print(f"File: {os.path.basename(file1)} to file: {os.path.basename(file2)} | Similarity: {sim*100:.2f}%")
                if sim > required_similarity:
                    similar_files.append(file2)
        
        if len(similar_files) >= 3:
            common_substring = os.path.commonprefix([os.path.basename(f) for f in similar_files])
            folder_name = common_substring.strip() or os.path.splitext(os.path.basename(file1))[0]
            folder_path = os.path.join(directory, folder_name)
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            for f in similar_files:
                os.rename(f, os.path.join(folder_path, os.path.basename(f)))

def process_new_file(directory, filename):
    matching_folder = bfs_folder_search(directory, filename)
    if matching_folder:
        sim = similarity(matching_folder, filename)
        print(f"File: {os.path.basename(filename)} to folder: {os.path.basename(matching_folder)} | Similarity: {sim*100:.2f}%")
        os.rename(filename, os.path.join(matching_folder, os.path.basename(filename)))
    else:
        with open("downloaded_files.txt", "r") as file:
            all_files = [line.split(",")[0].strip() for line in file.readlines()]
        all_files.append(filename)
        move_files_based_on_similarity(directory, all_files)

def process_directory(directory):
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path):
            print(f"Processing file: {filename}")
            process_new_file(directory, full_path)
        elif os.path.isdir(full_path):
            print(f"Descending into directory: {filename}")
            process_directory(full_path)

if __name__ == "__main__":
    directory = "./"  # adjust as needed

    if not any(os.path.isdir(os.path.join(directory, name)) for name in os.listdir(directory)):
        print("No directories found in the current location.")

    for website_folder in os.listdir(directory):
        website_path = os.path.join(directory, website_folder)
        if os.path.isdir(website_path):
            print(f"Processing directory: {website_folder}")
            process_directory(website_path)
