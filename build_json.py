import os, requests, json, zipfile, re
from extract import extract
from utils import hex_to_hash
from typing import Dict, Any

if os.path.exists('./rpkg'):
    print("rpkg folder already exists. Assuming that it's recent.")
else:
    # Download rpkg
    rpkg_tool_info = json.loads(requests.get('https://api.github.com/repos/glacier-modding/RPKG-Tool/releases/latest').text)
    download_links = [x['browser_download_url'] for x in rpkg_tool_info['assets'] if 'src' not in x['name']]
    if (len(download_links) != 1):
        print("Something went wrong with downloading rpkg, aborting.")
        exit()

    r = requests.get(download_links[0], stream=True)
    with open('rpkg.zip', 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

    with zipfile.ZipFile('rpkg.zip') as zf:
        zf.extractall('rpkg')

    os.remove('rpkg.zip')

mapping: Dict[int, str] = dict()

with open('./rpkg/hash_list.txt', 'r') as f:
    # completion
    f.readline()
    # hashes count
    f.readline()
    # version number
    f.readline()
    # actual lines
    for line in f.readlines():
        split = line.split(',')
        ioi_string = split[1].rstrip()
        hex = split[0][:-5]
        extension = split[0][:-4]

        mapping[hex_to_hash(hex)] = ioi_string

# File Directory
directory = "D:\\Program Files (x86)\\Epic Games\\HITMAN3\\Runtime"

# Open the directory and determine all of the possible rkpg files
rpkgs_names = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.rpkg')]

data: Dict[int, Dict[str, Any]] = dict()

print(rpkgs_names)

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
        if hash not in data:
            data[hash] = {
                'name': mapping[hash],
                'hex': rpkg.hashes_by_hash[hash].getHexName(),
                'type': rpkg.hashes_by_hash[hash].hash_resource_type,
                'depends': rpkg.hashes_by_hash[hash].getDependencies(),
                'chunks': [],
            }
        data[hash]['chunks'].append(chunk_num)

# Serializing json
json_object = json.dumps(data, indent=4)
 
# Writing to sample.json
with open("hashes.json", "w") as outfile:
    outfile.write(json_object)

print(data)