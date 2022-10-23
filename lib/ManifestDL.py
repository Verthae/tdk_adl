import os
from dataclasses import dataclass

base_url = "https://assets-danmakujp.cdn-dena.com"

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
