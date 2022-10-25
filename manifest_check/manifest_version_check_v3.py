import glob
import json
from zipfile import ZipFile
from dataclasses import dataclass, is_dataclass, asdict

save_directory = r""

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
    def save_path(self):
        return "https://assets-danmakujp.cdn-dena.com" + self.directory + self.hashpath

    @property
    def dl_path(self):
        return save_directory + self.directory[1:] + self.path

    def __eq__(self, other):
        if not isinstance(other, downloader):
            return NotImplemented
        # if not self.hash == other.hash and self.size == other.size:
        #     print(f"{self.hash} == {other.hash} : {str(self.hash == other.hash):>5s} and {self.size:>10} == {other.size:>10} : {self.size == other.size}")
        return self.hash == other.hash and self.size == other.size and self.hashpath == other.hashpath


def merge(dict1, dict2, json):
    for key in dict1:
        if key in dict2:
            # print(dict1[key] != dict2[key])
            if dict1[key] != dict2[key]:
                if key in comparing[json]:
                    if dict1[key] not in comparing[json][key]:
                        comparing[json][key].append(dict1[key])
                        comparing["filesize"] += dict1[key].size
                        comparing["filenum"] += 1
                else:
                    comparing[json][key] = [dict1[key]]
                    comparing["filesize"] += dict1[key].size
                    comparing["filenum"] += 1
        else:
            comparing[json][key] = [dict1[key]]
            comparing["filesize"] += dict1[key].size
            comparing["filenum"] += 1
    return {**dict1, **dict2}


manifest_list = sorted(glob.glob('**/arg_*.json', recursive=True), reverse=True)
for filename in manifest_list:
    with open(filename) as manifest_json:
        reader = json.load(manifest_json)
        manifest = {}
        for key in reader["manifest"]:
            manifest[key] = {
                x["AssetPath"]:
                    downloader(
                        x["AssetPath"], x["FileHash"], x["FileSize"], x["HashedPath"],
                        x["DownloadOption"], reader["assetDir"]
                    )
                for x in reader["manifest"][key]
            }
        for key in data:
            if str(key) in manifest:
                data[key] = merge(manifest[str(key)], data[key], key)

print(comparing["filenum"], ":", comparing["filesize"])
with open("list_v2.json", "w") as file:
    file.write(json.dumps(comparing, cls=EnhancedJSONEncoder))
