import requests
import json
import os
from lib import ASSET_UPLOAD_V2, MANIFESTS
from dataclasses import dataclass

base_url = "https://assets-danmakujp.cdn-dena.com"

os.makedirs(MANIFESTS, exist_ok=True)

@dataclass
class ManifestDL:
    root_path: str
    hash_path: str
    platform: str
    data_version: int
    enable: int
    db: str
    open_at: int
    salt: int

    @property
    def save_path(self):
        return os.path.join(self.root_path, 'data', self.hash_path)

    @property
    def dl_path(self):
        return '/'.join([base_url, 'assets', self.root_path, 'data', self.hash_path])


def get_manifests():
    manifest_dict = {} # for identifying duplicate manifests
    manifest_list = [] # for downloading
    for json_file in sorted(os.listdir(ASSET_UPLOAD_V2), reverse=True):
        with open(os.path.join(ASSET_UPLOAD_V2, json_file)) as f:
            uploads_list = json.loads(f.read())['Uploads']
            for uploads in uploads_list:
                root_path = uploads['Path']
                if root_path not in manifest_dict:
                    manifest_dict[root_path] = {}
                
                file_list = uploads['FileList']
                for file in file_list:
                    m = ManifestDL(root_path, file['HashPath'], file['Platform'],
                                   file['DataVersion'], file['Enable'], file['DB'],
                                   file['OpenAt'], file['Salt'])
                    if m.hash_path in manifest_dict[root_path]:
                        known_m = manifest_dict[root_path][m.hash_path]
                        if m != known_m:
                            raise Exception(f'{m} != {known_m}')
                    else:
                        manifest_dict[root_path][m.hash_path] = m
                        manifest_list.append(m)
    return manifest_list


def download(manifest):
    os.makedirs(os.path.dirname(os.path.join(MANIFESTS, manifest.save_path)), exist_ok=True)
    req_byte = bytearray(requests.get(manifest.dl_path).content)
    with open(os.path.join(MANIFESTS, manifest.save_path), "wb") as f:
        f.write(req_byte)
    print("Downloaded:", manifest.save_path)


if __name__ == "__main__":
    manifests = get_manifests()
    with open('manifests.txt', 'w') as f:
        for m in manifests:
            download(m)
            f.write(f'{m}\n')
    print("ALL DONE.")
