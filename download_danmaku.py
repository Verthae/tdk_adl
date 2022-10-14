import requests
import json
import os
from multiprocessing.pool import ThreadPool
import time
from lib import ASSETS, Encryptors, Keys

manf_url = "https://redive.estertion.win/dankagu_manifest/3700-20221012132424-a830.json"
base_url = "https://assets-danmakujp.cdn-dena.com"


os.makedirs(ASSETS, exist_ok=True)


def get_manf(url):
    req = requests.get(url).content
    return json.loads(req)


def download_them(l):
    os.makedirs(os.path.dirname(l[0]), exist_ok=True)
    req_byte = bytearray(requests.get(l[1]).content)
    # 1 and 2 are xab files - this runs the decryptor on them
    if l[3] in ["1", "2"]:
        Encryptors[Keys.DOWNLOAD_ASSETBUNDLE_KEY_1].modify(req_byte, 0, len(req_byte), 0, l[2] & 0xfff)
    # elif l[0].endswith(".dat"):   TODO
    #     Encryptors[Keys.DOWNLOAD_DAT_KEY].modify(req_byte, 0, len(req_byte), 0, l[2] & 0xfff)
    #     req_byte = Encryptors[Keys.DEFAULT_KEY].transform(req_byte, 0, len(req_byte))
    open(l[0], "wb").write(req_byte)
    print("Downloaded:", l[0])
    return l[5], l[4]["AssetPath"], l[4]["FileHash"]


def get_names(filtering):
    json_obj = get_manf(manf_url)
    assetdir = json_obj['assetDir']
    name_list = []
    for category, info in json_obj["manifest"].items():
        # 4 is db files
        # 3 is common - dat files and ACB/AWB files - filter out .dat if you just want audio files
        # 1 is Android xab files
        # 2 is iOS xab files
        # whichever files you don't want - uncomment below and put in the array
        if category in ["1", "2", "4"]:
            continue
        for names in info:
            # this filters out the .dat files from common - just uncomment the if to exclude them
            # there's some rijnael and gzip stuff necessary to extract them according to esterTion's php script
            if assetdir not in filtering or names['AssetPath'] not in filtering[adir]\
                    or filtering[assetdir][names['AssetPath']] != names['FileHash']:
                # if not names['AssetPath'].endswith('.dat'):
                    name_list.append((assetdir[1:]+names['AssetPath'], base_url+adir+names["HashedPath"],
                                      names["DownloadOption"], category, names, assetdir))
    return name_list


if __name__ == "__main__":
    # init()
    asset_list = {}
    asset_list_fp = os.path.join(ASSETS, "assetlist.txt")
    if os.path.exists(asset_list_fp):
        with open(asset_list_fp, "rt", encoding="utf8") as f:
            for line in f:
                adir, name, ahash = line.strip().split("\t")
                if adir not in asset_list:
                    asset_list[adir] = {}
                asset_list[adir][name] = ahash
            # asset_list = dict(line.strip().split("\t") for line in f if line.strip())
    lyst = get_names(asset_list)
    asset_list_f = open(asset_list_fp, "ab", buffering=0)

    results = ThreadPool(1).imap_unordered(download_them, lyst)
    for i, (adir, name, ahash) in enumerate(results):
        asset_list_f.write(f"{adir}\t{name}\t{ahash}\n".encode("utf8"))
        time.sleep(1)
    print("ALL DONE.")
    asset_list_f.close()
