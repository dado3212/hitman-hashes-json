import os, requests, json, re
from extract import extract
from utils import hex_to_hash, hash_to_hex, ioi_string_to_hex
from typing import Dict, Any
from Hash import Hash

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

mapping: Dict[int, str] = dict()

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

        mapping[hex_to_hash(hex)] = ioi_string

# File Directory
directory = "D:\\Program Files (x86)\\Epic Games\\HITMAN3\\Runtime"

# Open the directory and determine all of the possible rkpg files
rpkgs_names = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.rpkg')]

data: Dict[str, Dict[str, Any]] = dict()

print(rpkgs_names)

all_hashes: Dict[int, Hash] = dict()

# Download the raw TGA texture files
for rpkg_name in rpkgs_names:
    print("Looking at", rpkg_name)
    rpkg_path = os.path.join(directory, rpkg_name)
    rpkg = extract(rpkg_name, rpkg_path)
    if 'patch' in rpkg_name:
        chunk_info = re.search(r"chunk(\d+)patch(\d+)\.rpkg", rpkg_name, re.IGNORECASE)
        assert chunk_info is not None
        chunk_num = chunk_info.group(1) + '.' + chunk_info.group(2)
    else:
        chunk_info = re.search(r"chunk(\d+)\.rpkg", rpkg_name, re.IGNORECASE)
        assert chunk_info is not None
        chunk_num = chunk_info.group(1)

    for hash in rpkg.hashes_by_hash:
        if hash in all_hashes:
            all_hashes[hash].chunks.append(chunk_num)
        else:
            all_hashes[hash] = rpkg.hashes_by_hash[hash]
            all_hashes[hash].chunks = [chunk_num]

for hash in all_hashes:
    file = all_hashes[hash].getFormattedHash()
    data[file] = {
        'name': mapping[hash],
        'type': all_hashes[hash].hash_resource_type,
        'depends': [(all_hashes[x].getFormattedHash() if x in all_hashes else hash_to_hex(x)) for x in all_hashes[hash].getDependencies()],
        'chunks': all_hashes[hash].chunks,
        'correct_name': ioi_string_to_hex(mapping[hash]) == file
    }

# Serializing json
json_object = json.dumps(data, indent=4)
 
# Writing to sample.json
with open("hashes.json", "w") as outfile:
    outfile.write(json_object)
