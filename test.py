import os, math, numpy
from typing import List, Tuple
from lz4 import decompress
from extract import extract, chunkify_bytes, xtea_decrypt_localization, xor, symmetric_key_decrypt_localization 
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

# if rpkg.hashes[i].getFormattedHash() == '0083BDC30164F0DE':
#     print(raw_data)
#     print(rpkg_path)
#     print(rpkg.hashes[i].header.data_offset)
#     print(hash_size)
#     print(rpkg.hashes[i].lz4ed)
#     print(rpkg.hashes[i].xored)
#     print(rpkg.hashes[i].resource.size_final)
#     exit()

# And then uncomment and run the following:

# rpkg_name = 'chunk27.rpkg'
# print("Looking at", rpkg_name)
# rpkg_path = os.path.join(directory, rpkg_name)
# rpkg = extract(rpkg_name, rpkg_path)

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

rpkg_name = 'chunk27.rpkg'
rpkg_path = os.path.join(directory, rpkg_name)
f = open(rpkg_path, 'rb')
f.seek(37743234)
raw_data = bytearray(f.read(241))
raw_data = xor(raw_data, 241)
raw_bytes = decompress(raw_data, 617)
# print_bytes(raw_bytes) - confirm that we're correctly decoding to this point

# decode JSON
if (raw_bytes[0] == 0 or raw_bytes[0] == 1):
    position = 1
    number_of_languages = int((int.from_bytes(raw_bytes[position:position+4], 'little') - 1)/4)
    isLOCRv2 = True
else:
    position = 0
    number_of_languages = int(int.from_bytes(raw_bytes[position:position+4], 'little')/4)
    isLOCRv2 = False

# symmetric key cipher
symKey = (number_of_languages == 10 and not isLOCRv2)

offsets: List[int] = []
for i in range(number_of_languages):
    offset = int.from_bytes(raw_bytes[position:position+4], 'little')
    offsets.append(offset)
    position += 4

for i in range(number_of_languages):
    if offsets[i] == 0xFFFFFFFF:
        continue
    language_string_count = int.from_bytes(raw_bytes[position:position+4], 'little')
    position += 4
    print(language_string_count)

    for i in range(language_string_count):
        temp_language_string_hash = int.from_bytes(raw_bytes[position:position+4], 'little')
        position += 4

        temp_language_string_length = int.from_bytes(raw_bytes[position:position+4], 'little')
        position += 4

        print(temp_language_string_hash, temp_language_string_length, raw_bytes[position:position+temp_language_string_length])

        temp_string: List[Tuple[bytes, bytes]] = []
        for m in range(temp_language_string_length):
            temp_string.append(raw_bytes[position:position+1])
            position += 1
        print(temp_string)
        position += 1

        if symKey:
            # symmetric_key_decrypt_localization, ignoring for now
            string = ''.join([chr(symmetric_key_decrypt_localization(x)) for x in temp_string])
            print(string)
            continue
        else:
            string = None
            assert temp_language_string_length % 8 == 0
            for i in range(int(temp_language_string_length / 8)):
                print(i)
                one = temp_string[i*8:i*8+4]
                two = temp_string[i*8+4:i*8+8]
                print(one, two)
                a = xtea_decrypt_localization(temp_string[i*8:i*8 + 4], temp_string[i*8 + 4:i*8 + 8])
                print(a)
                if (string is None):
                    string = a[0] + a[1]
                else:
                    string += a[0] + a[1]
                print()
            print(string.decode('utf-8'))
