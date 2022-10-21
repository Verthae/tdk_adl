import glob
import os
import json
import time

import requests
from lib import RAW
from dataclasses import dataclass, is_dataclass, asdict

base_url = "https://assets-danmakujp.cdn-dena.com"

os.makedirs(RAW, exist_ok=True)

save_directory = os.path.join(RAW, "unique_raw")
os.makedirs(os.path.dirname(save_directory), exist_ok=True)

manifest_list = sorted(glob.glob("[0-90-90-90-9]*.json"), reverse=True)
use_hash = True
compiled_list = json.loads(open("list.json", "r").read())
session_size = 0
session_files = 0

data = {
    "1": {},
    "2": {},
    "3": {},
    "4": {},
}
comparing = {
    "1": {},
    "2": {},
    "3": {},
    "4": {},
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
        return save_directory + ("\\data" + self.hashpath) if use_hash else (self.directory + self.path)

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
    os.makedirs(os.path.dirname(asset_data.save_path), exist_ok=True)
    req_byte = requests.get(asset_data.dl_path)
    if req_byte.status_code != "404":
        with open(asset_data.save_path, "wb") as f:
            f.write(bytearray(req_byte.content))
        print("Downloaded:", asset_data.save_path)
    else:
        print(asset_data.dl_path, " was not found.")
    return req_byte.status_code != "404"


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



# Read any additional manifests - compare and include into downloader dictionary
for filename in manifest_list:
    manifest_json = open(filename, 'r')
    reader = json.load(manifest_json)
    manifest = {}
    for index in reader["manifest"]:
        manifest[index] = {
            x["AssetPath"]:
                downloader(
                    x["AssetPath"], x["FileHash"], x["FileSize"], x["HashedPath"],
                    x["DownloadOption"], reader["assetDir"]
                )
            for x in reader["manifest"][index]
        }
    for index in manifest:
        if index in data:
            data[index] = merge(manifest[index], data[index], index)

# Read download history
previously_downloaded = []
downloaded_list_fp = os.path.join(RAW, "unique_assets.txt")
if os.path.exists(downloaded_list_fp):
    with open(downloaded_list_fp) as reader:
        previously_downloaded = [line.strip() for line in reader.readlines()]
cur_progress = len(previously_downloaded)

# Append new file hashes to history, download new files
with open(os.path.join(RAW, "unique_assets.txt"), 'a') as writer:
    for index in comparing:
        if isinstance(comparing[index], dict):
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
