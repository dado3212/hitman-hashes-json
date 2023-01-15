import os, requests, json
from utils import ioi_string_to_hex
from typing import Dict, Any

try:
    os.remove('./hash_list.txt')
except OSError:
    pass

# Download latest hashes
r = requests.get('https://hitmandb.notex.app/latest-hashes.7z', stream=True)
with open('latest-hashes.7z', 'wb') as fd:
    for chunk in r.iter_content(chunk_size=128):
        fd.write(chunk)

# Fix this for your setup
os.system('"C:\\Program Files\\7-Zip\\7z.exe" e ./latest-hashes.7z')

os.remove('./latest-hashes.7z')

mapping: Dict[str, str] = dict()

with open('./hash_list.txt', 'r') as f:
    # completion
    f.readline()
    # hashes count
    f.readline()
    # version number
    f.readline()
    # actual lines
    for line in f.readlines():
        split = line.split(',', 1)
        ioi_string = split[1].rstrip()
        hex = split[0][:-5]
        extension = split[0][:-4]

        mapping[hex] = ioi_string

with open('hashes.json', 'r') as f:
    data: Dict[str, Any] = json.load(f)

for hash in mapping:
    if hash in data and not data[hash]['correct_name'] and ioi_string_to_hex(mapping[hash]) == hash:
        data[hash]['name'] = mapping[hash]
        data[hash]['correct_name'] = True

# Serializing json
json_object = json.dumps(data, indent=4)
 
# Writing to hashes.json
with open("hashes.json", "w") as outfile:
    outfile.write(json_object)
