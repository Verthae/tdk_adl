import json
import os
import zlib
from lib import ASSET_UPLOAD_V2, MANIFESTS, Encryptors, Keys, ManifestDL
from D4L.TakashoFes.Master.AssetPathRaw import AssetPathRaw

if __name__ == '__main__':
    manifest_dict = {}
    for json_file in sorted(os.listdir(ASSET_UPLOAD_V2), reverse=True):
        with open(os.path.join(ASSET_UPLOAD_V2, json_file)) as f:
            uploads_list = json.loads(f.read())['Uploads']
            for uploads in uploads_list:
                root_path = uploads['Path']
                file_list = uploads['FileList']
                for file in file_list:
                    m = ManifestDL(root_path, file['HashPath'], file['Platform'],
                                   file['DataVersion'], file['Enable'], file['DB'],
                                   file['OpenAt'], file['Salt'])
                    
                    # decrypt downloaded manifest
                    data = bytearray()
                    with open(os.path.join(MANIFESTS, m.save_path), 'rb') as fin:
                        data = bytearray(fin.read())
                        Encryptors(Keys.EMBEDED_FILELIST_KEY).modify(data, 0, len(data), 0, m.salt)
                        data = Encryptors(Keys.EMBEDED_AES_KEY).transform(data, 0, len(data))
                        data = zlib.decompress(data, 16+zlib.MAX_WBITS)
                        data = data[512:]
                    
                    # compare manifests based on root path & DB 
                    key = root_path + '/' + m.db
                    if key not in manifest_dict:
                        manifest_dict[key] = 1
                    else:
                        raise Exception(f'Found duplicate key {key}')
                    
                    # convert flatbuffer to json
                    json_data = {'assetDir': '/assets/' + root_path + '/data',
                                 'manifest': {'1':[], '2':[], '3':[], '4':[]}}
                    assetPathRaw = AssetPathRaw.GetRootAs(data, 0)
                    for i in range(assetPathRaw.EntriesLength()):
                        e = assetPathRaw.Entries(i)
                        category = e.HashedPath().decode('ascii')[1:2]
                        json_entry = {
                            'ID': e.Id(),
                            'AssetPath': e.AssetPath().decode('ascii'),
                            'HashedPath': e.HashedPath().decode('ascii'),
                            'FileHash': e.FileHash().decode('ascii'),
                            'FileSize': e.FileSize(),
                            'FileRev': e.FileRev(),
                            'FileType': e.FileType(),
                            'DownloadOption': e.DownloadOption()
                        }
                        json_data['manifest'][category].append(json_entry)
                    
                    # save json
                    save_file = os.path.join(MANIFESTS, 'decrypted', key + '.json')
                    os.makedirs(os.path.dirname(save_file), exist_ok=True)
                    with open(save_file, 'w') as fout:
                        fout.write(json.dumps(json_data, separators=(',', ':')))
