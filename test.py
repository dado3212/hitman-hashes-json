import os, math, numpy
from extract import extract
from lz4 import decompress
from extract import chunkify_bytes, xor

# Load lz4

# Test function for messing around with logic

# File Directory
directory = "D:\\Program Files (x86)\\Epic Games\\HITMAN3\\Runtime"

rpkg_name = 'chunk28.rpkg'
print("Looking at", rpkg_name)
rpkg_path = os.path.join(directory, rpkg_name)
# rpkg = extract(rpkg_name, rpkg_path)

f = open(rpkg_path, 'rb')
f.seek(397464619)
raw_data = bytearray(f.read(60))

raw_data = xor(raw_data, 60)
print(raw_data)
f = decompress(raw_data, 64)
print(f)
print(chunkify_bytes(f, 64))

# if rpkg.hashes[i].getFormattedHash() == '006ABC35562F09D2':
#     print(raw_data)
#     print(chunkify_bytes(raw_data, hash_size))
#     print(rpkg_path)
#     print(rpkg.hashes[i].header.data_offset)
#     print(60)
#     print(rpkg.hashes[i].resource.size_final)


# Looking at chunk28.rpkg
# b'\xf2\r$\x00\x00\x00Play_CIN_SFX_ExitCut_Boa\x05\x00\xf3\x00house\x00\x00\x00\x80\xbf\x00\x00\x00\x00\x01\x04\x00\x80\x8e)\x13\x00\x00\x00\x00\x00'
# ['Play_CIN_SFX_ExitCut_Boa']
# D:\Program Files (x86)\Epic Games\HITMAN3\Runtime\chunk28.rpkg
# 397464619
# 60
# 64