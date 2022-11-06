import os, math, numpy
from typing import List, Tuple
from lz4 import decompress
from extract import extract, chunkify_bytes, xor, decode_locr_to_json_strings, xtea_decrypt_localization, decode_dlge_to_string
from utils import print_bytes

# Test functions for messing around with logic

########
# Global
########
directory = "D:\\Program Files (x86)\\Epic Games\\HITMAN3\\Runtime"

########
# Offset
########

# Add the following for whatever hash you want to analyze to extract.py before the chunkify piece

# if rpkg.hashes[i].getFormattedHash() == '000ECD34A5D5DD7D':
#     print(raw_data)
#     print(rpkg_path)
#     print(rpkg.hashes[i].header.data_offset)
#     print(hash_size)
#     print(rpkg.hashes[i].lz4ed)
#     print(rpkg.hashes[i].xored)
#     print(rpkg.hashes[i].resource.size_final)
#     exit()

# And then uncomment and run the following:

rpkg_name = 'chunk28.rpkg'
print("Looking at", rpkg_name)
rpkg_path = os.path.join(directory, rpkg_name)
rpkg = extract(rpkg_name, rpkg_path)

########
# LZ4 - 006ABC35562F09D2
########

# rpkg_name = 'chunk28.rpkg'
# rpkg_path = os.path.join(directory, rpkg_name)
# f = open(rpkg_path, 'rb')
# f.seek(397464619)
# raw_data = bytearray(f.read(60))

# raw_data = xor(raw_data, 60)
# print(raw_data)
# f = decompress(raw_data, 64)
# print(f)
# print(chunkify_bytes(f, 64))

########
# LOCR - 0083BDC30164F0DE
########

# rpkg_name = 'chunk27.rpkg'
# rpkg_path = os.path.join(directory, rpkg_name)
# f = open(rpkg_path, 'rb')
# f.seek(37743234)
# raw_data = bytearray(f.read(241))
# raw_data = xor(raw_data, 241)
# raw_bytes = decompress(raw_data, 617)
# # print_bytes(raw_bytes) - confirm that we're correctly decoding to this point

# # decode JSON
# print(decode_locr_to_json_strings(raw_bytes))

########
# DLGE - 00B68C63029BFD05
########

# rpkg_name = 'chunk23.rpkg'
# rpkg_path = os.path.join(directory, rpkg_name)
# f = open(rpkg_path, 'rb')
# f.seek(47846495)
# raw_data = bytearray(f.read(1351))
# raw_data = xor(raw_data, 1351)
# raw_bytes = decompress(raw_data, 1383)

# # DLGE specific
# print(decode_dlge_to_string(raw_bytes))

        