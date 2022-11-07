import glob
import os
import json
import time

import requests
from lib import RAW, LIST, DECRYPT, Encryptors, Keys
from dataclasses import dataclass, is_dataclass, asdict

base_url = "https://assets-danmakujp.cdn-dena.com"

os.makedirs(RAW, exist_ok=True)
os.makedirs(DECRYPT, exist_ok=True)

#Ask for onput on how to save the files
ask = input("Do you want to save via hash path? (Leave blank for no)")
use_hash = True if ask == 'y' else False
ask = input("Do you want to decrypt the game assets? (Leave blank for no)")
decode = True if ask == 'y' else False
ask = input("Do you want to filter the download sections? (Leave blank for no, select 1234)")
dlfilter = ask

compiled_list = json.loads(open(os.path.join(LIST, "list_v3.json"), "r").read())
session_size = 0
session_files = 0

save_directory = DECRYPT if decode else os.path.join(RAW, "unique_raw")
os.makedirs(os.path.dirname(save_directory), exist_ok=True)

data = {
    "1": {},
    "2": {},
    "3": {},
    "4": {},
}

comparing = {
    "1": {},  # Android
    "2": {},  # iOS
    "3": {},  # Audio / Scenario Data
    "4": {},  # Master Data
    "filesize": 0,
    "filenum": 0
}


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


@dataclass
class downloader:
    path: str
    hash: str
    size: int
    hashpath: str
    option: int
    directory: str

    @property
    def dl_path(self):
        return base_url + self.directory + self.hashpath

    @property
    def save_path(self):
        # print(self.path.rsplit("/", 1))
        dir, file = self.path.rsplit("/", 1)
        modified_dir = os.path.join(dir, self.hash, file)
        print(save_directory)
        return save_directory + (("\\data" + self.hashpath) if use_hash else (self.directory + modified_dir))

    def __eq__(self, other):
        if not isinstance(other, downloader):
            return NotImplemented
        return self.hash == other.hash and self.size == other.size and self.hashpath == other.hashpath

    def __repr__(self):
        return self.dl_path


# Convert saved downloader asdict() back to downloader class
def dict_to_download(dictm):
    return downloader(dictm["path"], dictm["hash"], dictm["size"], dictm["hashpath"], dictm["option"], dictm["directory"])


def download(asset_data):
    dl_directory = asset_data.save_path
    os.makedirs(os.path.dirname(asset_data.save_path), exist_ok=True)
    req_byte = requests.get(asset_data.dl_path)
    if req_byte.status_code == 200:
        with open(dl_directory, "wb") as f:
            filedata = bytearray(req_byte.content)
            if decode and asset_data.hashpath[1] in ["1", "2"]:
                Encryptors[Keys.DOWNLOAD_ASSETBUNDLE_KEY_1].modify(
                    filedata, 0, len(filedata), 0, asset_data.option & 0xfff)
            f.write(filedata)
        print("Downloaded:", dl_directory)
    else:
        print(asset_data.dl_path, " was not found.")
    return req_byte.status_code == 200


def merge(dict1, dict2, json_id):
    global change
    for prefix in dict1:
        if prefix in dict2:
            if dict1[prefix] != dict2[prefix]:
                if prefix in comparing[json_id]:
                    if dict1[prefix] not in comparing[json][prefix]:
                        comparing[json][prefix].append(dict1[prefix])
                        # comparing["filesize"] += dict1[prefix].size
                        # comparing["filenum"] += 1
                        # change += 1
                else:
                    comparing[json][prefix] = [dict1[prefix]]
                    # comparing["filesize"] += dict1[prefix].size
                    # comparing["filenum"] += 1
                    # change += 1
    return {**dict1, **dict2}


# Populate data from list.json - precompiled list of unique files into downloader dictionary
for asset_path in comparing:
    if isinstance(comparing[asset_path], dict):
        for folder in compiled_list[asset_path]:
            comparing[asset_path][folder] = []
            for version in compiled_list[asset_path][folder]:
                comparing[asset_path][folder].append(dict_to_download(version))
    else:
        comparing[asset_path] = compiled_list[asset_path]

# Read download history
previously_downloaded = []
downloaded_list_fp = os.path.join(RAW, "unique_assets.txt")
if os.path.exists(downloaded_list_fp):
    with open(downloaded_list_fp) as reader:
        previously_downloaded = [line.strip() for line in reader.readlines()]
cur_progress = len(previously_downloaded)

# Append new file hashes to history, download new files
with open(os.path.join(DECRYPT if decode else RAW, "unique_assets.txt"), 'a') as writer:
    for index in comparing:
        if isinstance(comparing[index], dict) and index not in dlfilter:
            for asset in comparing[index]:
                for file_download in comparing[index][asset]:
                    if file_download.hashpath not in previously_downloaded:
                        if download(file_download):
                            writer.write(file_download.hashpath + "\n")
                            session_size += file_download.size
                            session_files += 1
                            cur_progress += 1
                            time.sleep(1)
                            print(f"Progress: {cur_progress:>5d} of {comparing['filenum']} - {session_files:>5d} files this session)")


print(f"Total Download: {comparing['filesize']}, {comparing['filenum']}")
print(f"Session Download: {session_size}, Session Files: {session_files})")
