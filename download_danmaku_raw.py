import requests
import json
import os
from multiprocessing.pool import ThreadPool
import time
from lib import ROOT, RAW, Encryptors, Keys
from dataclasses import dataclass

manf_url = "https://redive.estertion.win/dankagu_manifest/3700-20221012132424-a830.json"
base_url = "https://assets-danmakujp.cdn-dena.com"

os.makedirs(RAW, exist_ok=True)

@dataclass
class AssetDL:
    category: int
    path: str
    hashpath: str
    filehash: str
    option: int
    directory: str

    @property
    def save_path(self):
        return self.directory[1:] + self.path

    @property
    def dl_path(self):
        return base_url + self.directory + self.path

    @property
    def log_data(self):
        return self.directory, self.path, self.filehash

def get_manf(url):
    req = requests.get(url).content
    return json.loads(req)


def download_them(asset):
    os.makedirs(os.path.dirname(os.path.join(RAW, asset.save_path)), exist_ok=True)
    req_byte = bytearray(requests.get(asset.dl_path).content)
    open(os.path.join(RAW, asset.save_path), "wb").write(req_byte)
    print("Downloaded:", asset.save_path)
    return asset.log_data  # l[5], l[4]["AssetPath"], l[4]["FileHash"]


def get_names(filtering):
    json_obj = get_manf(manf_url)
    assetdir = json_obj['assetDir']
    name_list = []
    for category, info in json_obj["manifest"].items():
        for names in info:
            if assetdir not in filtering or names['AssetPath'] not in filtering[assetdir]\
                    or filtering[assetdir][names['AssetPath']] != names['FileHash']:
                name_list.append(AssetDL(category, names['AssetPath'], names['HashedPath'], names['FileHash'],
                                         names['DownloadOption'], assetdir))
    return name_list


if __name__ == "__main__":
    asset_list = {}
    asset_list_fp = os.path.join(RAW, "assetlist.txt")
    if os.path.exists(asset_list_fp):
        with open(asset_list_fp, "rt", encoding="utf8") as f:
            for line in f:
                adir, name, ahash = line.strip().split("\t")
                if adir not in asset_list:
                    asset_list[adir] = {}
                asset_list[adir][name] = ahash
    lyst = get_names(asset_list)
    asset_list_f = open(asset_list_fp, "ab", buffering=0)

    results = ThreadPool(1).imap_unordered(download_them, lyst)
    for i, (adir, name, ahash) in enumerate(results):
        asset_list_f.write(f"{adir}\t{name}\t{ahash}\n".encode("utf8"))
        time.sleep(1)
    print("ALL DONE.")
    asset_list_f.close()
