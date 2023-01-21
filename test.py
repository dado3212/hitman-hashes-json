import os, math, numpy
from typing import List, Tuple
from lz4 import decompress
from extract import extract, chunkify_bytes, xor, decode_locr_to_json_strings, xtea_decrypt_localization, decode_dlge_to_string, decode_rtlv_to_json_strings
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

# if rpkg.hashes[i].getFormattedHash() == '002D4F19DCD209F1':
#     print(raw_data)
#     print(rpkg_path)
#     print(rpkg.hashes[i].header.data_offset)
#     print(hash_size)
#     print(rpkg.hashes[i].lz4ed)
#     print(rpkg.hashes[i].xored)
#     print(rpkg.hashes[i].resource.size_final)
#     exit()

# And then uncomment and run the following:

# rpkg_name = 'chunk28.rpkg'
# print("Looking at", rpkg_name)
# rpkg_path = os.path.join(directory, rpkg_name)
# rpkg = extract(rpkg_name, rpkg_path)

########
# WSWB - 00F678A0DE445545
########

# rpkg_name = 'chunk0.rpkg'
# rpkg_path = os.path.join(directory, rpkg_name)
# f = open(rpkg_path, 'rb')
# f.seek(22942730)
# raw_data = bytearray(f.read(121))

# raw_data = xor(raw_data, 121)
# print(raw_data)
# f = decompress(raw_data, 172)
# print(f)
# print(chunkify_bytes(f, 172, 'WSWB'))

########
# MATI - 00615023F867E70E (short string extraction)
########

# rpkg_name = 'chunk1patch2.rpkg'
# rpkg_path = os.path.join(directory, rpkg_name)
# f = open(rpkg_path, 'rb')
# f.seek(506954228)
# raw_data = bytearray(f.read(868))

# raw_data = xor(raw_data, 868)
# print(raw_data)
# f = decompress(raw_data, 2624)
# print(f)
# print(chunkify_bytes(f, 2624, 'MATI'))

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
# # print_bytes(raw_bytes) #  confirm that we're correctly decoding to this point

# # # decode JSON
# print(decode_locr_to_json_strings(raw_bytes))

########
# LINE - 0012402F364E8A65
########

# rpkg_name = 'chunk27.rpkg'
# rpkg_path = os.path.join(directory, rpkg_name)
# f = open(rpkg_path, 'rb')
# f.seek(37743475)
# raw_data = bytearray(f.read(5))
# raw_data = xor(raw_data, 5)
# print(int.from_bytes(raw_data[0:4], 'little')) # 3735784903 -> need to go through LOCR to figure out what it is

########
# DLGE - 00B68C63029BFD05
########

# Hyphen within block ; seek - 78174598, size 3520, unpacked 3575

# rpkg_name = 'chunk28.rpkg'
# rpkg_path = os.path.join(directory, rpkg_name)
# f = open(rpkg_path, 'rb')
# f.seek(420308766)
# raw_data = bytearray(f.read(2472))
# raw_data = xor(raw_data, 2472)
# raw_bytes = decompress(raw_data, 2535)

# # DLGE specific
# print(decode_dlge_to_string(raw_bytes))

########
# RTLV - 00DDA871EA200CCF
########

# rpkg_name = 'chunk28.rpkg'
# rpkg_path = os.path.join(directory, rpkg_name)
# f = open(rpkg_path, 'rb')
# f.seek(2052427504)
# raw_data = bytearray(f.read(31167))
# raw_data = xor(raw_data, 31167)
# raw_bytes = decompress(raw_data, 33664)

# # decode JSON
# print(decode_rtlv_to_json_strings(raw_bytes))