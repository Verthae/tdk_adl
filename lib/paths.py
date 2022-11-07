import os
#  Modify ROOT to whatever directory you want to store in - default is the same folder that holds lib
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
ASSET_UPLOAD_V2 = os.path.join(ROOT, "AssetUploadV2")
MANIFESTS = os.path.join(ROOT, "manifests")
ASSETS = os.path.join(ROOT, "assets")
RAW = os.path.join(ROOT, "raw")
DECRYPT = os.path.join(ROOT, "decrypt")
LIST = os.path.join(ROOT, "manifest_check")
