import requests
import json
import os
from multiprocessing.pool import ThreadPool
import struct
import time
from lib import ASSETS

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
        modify(req_byte, 0, len(req_byte), 0, l[2] & 0xfff)
    open(l[0], "wb").write(req_byte)
    print("Downloaded:", l[0])
    return l[5], l[4]["AssetPath"], l[4]["FileHash"]

y = 0x051c1d53
swizzle_bytes = b''
coef = 0
offset = 0


def init():
    global coef, offset
    init_spin = 17
    while init_spin > 0:
        next()
        init_spin -= 1
    make_swizzle_table()
    coef = (next() & 0xf) + 3
    offset = (next() & 0x1f) + 1


def modify(data_bytes, _offset, count, stream_offset, salt):
    global swizzle_bytes, coef, offset
    mask = len(swizzle_bytes) - 1
    for i in range(count):
        b = data_bytes[_offset + i]
        swizzle_index = (offset + (stream_offset + _offset + salt + i) * coef) & mask
        if swizzle_index >= len(swizzle_bytes):
            raise Exception('swizzle_index out of range')
        data_bytes[_offset + i] = (swizzle_bytes[swizzle_index] ^ b) & 0xff


def next():
    global y
    x = (y ^ ((y << 13) & 0xffffffff)) & 0xffffffff
    x = (x ^ ((x >> 17) & 0xffffffff)) & 0xffffffff
    y = (x ^ ((32 * x) & 0xffffffff)) & 0xffffffff
    return y


def make_swizzle_table():
    global swizzle_bytes
    table_size = 512
    for i in range(table_size):
        result = next()
        swizzle_bytes += struct.pack("B", (result >> 3) & 0xff)


def get_names(filter):
    jsonObj = get_manf(manf_url)
    dir = jsonObj['assetDir']
    name_list = []
    for category, info in jsonObj["manifest"].items():
        # 4 is db files
        # 3 is common - dat files and ACB/AWB files - filter out .dat if you just want audio files
        # 1 is Android xab files
        # 2 is iOS xab files
        # whichever files you don't want - uncomment below and put in the array
        # if category in ["1", "3", "4"]:
        #     continue
        for names in info:
            # this filters out the .dat files from common - just uncomment the if to exclude them
            # there's some rijnael and gzip stuff necessary to extract them according to esterTion's php script
            if dir not in filter or names['AssetPath'] not in filter[dir] or filter[dir][names['AssetPath']] != names['FileHash']:
                # if not names['AssetPath'].endswith('.dat'):
                    name_list.append((dir[1:]+names['AssetPath'], base_url+dir+names["HashedPath"],
                                      names["DownloadOption"], category, names, dir))
    return name_list


if __name__ == "__main__":
    init()
    asset_list = {}
    asset_list_fp = os.path.join(ASSETS, "assetlist.txt")
    if os.path.exists(asset_list_fp):
        with open(asset_list_fp, "rt", encoding="utf8") as f:
            for line in f:
                dir, name, ahash = line.strip().split("\t")
                if dir not in asset_list:
                    asset_list[dir] = {}
                asset_list[dir][name] = ahash
            # asset_list = dict(line.strip().split("\t") for line in f if line.strip())
    lyst = get_names(asset_list)
    asset_list_f = open(asset_list_fp, "ab", buffering=0)

    # Modify ThreadPool() for what works best for you - my connection is slow
    results = ThreadPool(1).imap_unordered(download_them, lyst)
    for i, (dir, name, ahash) in enumerate(results):
        asset_list_f.write(f"{dir}\t{name}\t{ahash}\n".encode("utf8"))
        time.sleep(1)
    print("ALL DONE.")
