from os.path import getsize
from typing import List, Union, Tuple, Optional, Dict
from Hash import Hash, HashHeader, HashResource, HashReferenceData
from RPKG import RPKG, Header
import numpy, math
from lz4 import decompress
import ctypes

xor_array = bytearray([0xDC, 0x45, 0xA6, 0x9C, 0xD3, 0x72, 0x4C, 0xAB])

def xor(raw_data: bytearray, length: int) -> bytearray:
    # Adapted from crypto::xor_data
    # https://github.com/glacier-modding/RPKG-Tool/blob/344f6a9c73abe41edfda427e17ed2aa4189fdb3e/rpkg_src/crypto.cpp#L9

    # Key multiplication in order to match the data length
    key = (xor_array*int(math.ceil(float(length)/8.0)))[:length]
    return (numpy.bitwise_xor(raw_data, key)).tobytes()

def symmetric_key_decrypt_localization(value: int) -> int:
    # Adapted from crypto::symmetric_key_decrypt_localization
    # https://github.com/glacier-modding/RPKG-Tool/blob/48f01af7cbc1b782473f1ab24362cca913c9686a/src/crypto.cpp#L84
    bits = [value & 1, (value & 2) >> 1, (value & 4) >> 2, (value & 8) >> 3, (value & 16) >> 4, (value & 32) >> 5, (value & 64) >> 6, (value & 128) >> 7]
    output = (bits[0] << 0) | (bits[1] << 4) | (bits[2] << 1) | (bits[3] << 5) | (bits[4] << 2) | (bits[5] << 6) | (bits[6] << 3) | (bits[7] << 7)
    return output ^ 226

l10n_key: List[int] = [0x53527737, 0x7506499E, 0xBD39AEE3, 0xA59E7268]
l10n_delta = 0x9E3779B9

def xtea_decrypt_localization(v0_init: bytes, v1_init: bytes) -> Tuple[bytes, bytes]:
    # Adapted from crypto::xtea_decrypt_localization
    # https://github.com/glacier-modding/RPKG-Tool/blob/48f01af7cbc1b782473f1ab24362cca913c9686a/src/crypto.cpp#L34
    sum = 0xC6EF3720
    v0 = ctypes.c_uint32(int.from_bytes(v0_init, byteorder='little'))
    v1 = ctypes.c_uint32(int.from_bytes(v1_init, byteorder='little'))
    for _ in range(32): # num_rounds
        v1.value -= (v0.value << 4 ^ v0.value >> 5) + v0.value ^ sum + l10n_key[sum >> 11 & 3]
        sum -= l10n_delta
        v0.value -= (v1.value << 4 ^ v1.value >> 5) + v1.value ^ sum + l10n_key[sum & 3]

    return (v0.value.to_bytes(4, byteorder='little'), v1.value.to_bytes(4, byteorder='little'))

def chunkify_bytes(raw_data: Union[bytearray,bytes], length: int, resource_type: str, min_size: int = 10) -> List[str]:
    # Doesn't filter out ALL of the junk, but it does an okay job
    # if chunk_size > 20 or re.match(r'.*([A-Z]{4}|[a-z]{4}).*', current_chunk):

    # Nothing useful
    if resource_type in ['TEXD', 'PRIM', 'WWEM', 'VTXD', 'TEXT', 'MJBA', 'ALOC', 'WBNK', 'SCDA', 'GFXI', 'SDEF']:
        return []
    elif resource_type in ['RTLV']:
        # TODO: Convert this to JSON extraction
        # TODO: Also do the same for REPO (and ORES?)
        return []
    # Didn't check for use, but they're big and I think it's useless
    elif resource_type in ['NAVP', 'AIRG']:
        return []
    # Only has useful data in the beginning...I think
    elif resource_type in ['GFXV', 'WWEV', 'WWES']:
        max_length = 5000
    # this scares me
    elif resource_type == 'BOXC':
        max_length = 5000
    elif resource_type in ['TBLU', 'TEMP']:
        # TODO: Should be able to skip to FF FF FF FF FF FF sections if we're
        # worried
        max_length = 1000000
    # kind of just useful in general, keep it big (ATMD, ECPB, FXAS, MATB, MATI are all small) (MATI might be only useful at the beginning)
    elif resource_type in ['BORG', 'ASVA', 'ATMD', 'ECPB', 'FXAS', 'MATB']:
        max_length = 1000000
    elif resource_type in ['MATI']:
        max_length = 1000000
        min_size = 6
    elif resource_type in ['MATE', 'GFXF', 'MRTN']:
        # TODO: Data at the beginning and the end, can we excise the middle?
        max_length = 1000000
    # Good through the whole thing, but could probably be kept small
    elif resource_type in ['ATMD']:
        max_length = 1000000
    # turn on little strings for these two
    elif resource_type in ['DSWB', 'WSWB']:
        max_length = 1000000
        min_size = 3
    else:
        max_length = 1000000

    chunks: List[str] = []
    current_pos = 0
    i = 0
    for i in range(min(length, max_length)):
        if 32 <= raw_data[i] <= 126:
            continue
        else:
            if (i - current_pos) >= min_size:
                chunks.append((raw_data[current_pos:i]).decode('utf-8'))
            current_pos = i + 1
    if length < max_length and (length - current_pos) >= min_size:
        chunks.append((raw_data[current_pos:]).decode('utf-8'))
    return chunks

def flatten_locr_dict_to_set(input: Dict[int, set[str]]) -> List[str]:
    strings: set[str] = set()
    for key in input:
        for string in input[key]:
            strings.add(string)
    return list(strings)

def decode_locr_to_json_strings(raw_bytes: bytes) -> Dict[int, set[str]]:
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

    all_strings: Dict[int, set[str]] = {}
    # This can go up to number_of_languages but we only care about the first two, xx and en
    for i in range(2):
        if offsets[i] == 0xFFFFFFFF:
            continue
        language_string_count = int.from_bytes(raw_bytes[position:position+4], 'little')
        position += 4

        for i in range(language_string_count):
            temp_language_string_hash = int.from_bytes(raw_bytes[position:position+4], 'little')
            position += 4

            temp_language_string_length = int.from_bytes(raw_bytes[position:position+4], 'little')
            position += 4

            temp_string = raw_bytes[position:position+temp_language_string_length]
            position += temp_language_string_length + 1

            if symKey:
                # symmetric_key_decrypt_localization, ignoring for now
                if temp_language_string_hash not in all_strings:
                    all_strings[temp_language_string_hash] = set()
                all_strings[temp_language_string_hash].add(''.join([chr(symmetric_key_decrypt_localization(x)) for x in temp_string]))
            else:
                string = None
                assert temp_language_string_length % 8 == 0
                for i in range(int(temp_language_string_length / 8)):
                    a = xtea_decrypt_localization(temp_string[i*8:i*8 + 4], temp_string[i*8 + 4:i*8 + 8])
                    if (string is None):
                        string = a[0] + a[1]
                    else:
                        string += a[0] + a[1]
                if string is not None:
                    if temp_language_string_hash not in all_strings:
                        all_strings[temp_language_string_hash] = set()
                    all_strings[temp_language_string_hash].add(string.decode('utf-8').strip('\x00'))
    return all_strings

def decode_dlge_to_string(raw_bytes: bytes) -> Optional[str]:
    assert raw_bytes[0] == 0
    assert raw_bytes[4] == 1
    position = 8

    text_available = (int.from_bytes(raw_bytes[position:position+1], 'little') == 1)
    position += 1

    number_of_dlge_categories = 0
    if text_available:
        number_of_dlge_categories += 1
        # category = int.from_bytes(raw_bytes[position:position+4], 'little')
        position += 4
        # identifier = int.from_bytes(raw_bytes[position:position+4], 'little')
        position += 4

        # Mirroring the C++ code w/o the validation
        position += 4 + 8 + 4

        check = int.from_bytes(raw_bytes[position:position+4], 'little')
        if check == 0:
            position += 4

        check1 = int.from_bytes(raw_bytes[position:position+4], 'little')
        position += 4
        check2 = int.from_bytes(raw_bytes[position:position+4], 'little')
        position += 4

        assert (check1 == 0xFFFFFFFF and check2 == 0xFFFFFFFF) or ((check1 + 1) == check2) or check2 == 0xFFFFFFFF

        # en is first
        temp_language_string_sizes = int.from_bytes(raw_bytes[position:position+4], 'little')
        position += 4

        temp_string = raw_bytes[position:position+temp_language_string_sizes]
        position += temp_language_string_sizes + 1

        string = None
        assert temp_language_string_sizes % 8 == 0
        for i in range(int(temp_language_string_sizes / 8)):
            a = xtea_decrypt_localization(temp_string[i*8:i*8 + 4], temp_string[i*8 + 4:i*8 + 8])
            if (string is None):
                string = a[0] + a[1]
            else:
                string += a[0] + a[1]
        if string is not None:
            return string.decode('utf-8').strip('\x00')
    return None

def extract(rpkg_name: str, rpkg_path: str):
    rpkg = RPKG(rpkg_name, rpkg_path)

    # Load up the RPKG
    # Adapted from import_rpkg in RPKG-Tool
    f = open(rpkg_path, 'rb')
    
    file_size = getsize(rpkg_path)

    # Read the version
    raw_version = f.read(4)
    if (raw_version.decode("utf-8")  == 'GKPR'):
        rpkg.version = 1
    elif (raw_version.decode("utf-8")  == '2KPR'):
        rpkg.version = 2
        rpkg.v2_header = f.read(9)
    else:
        exit("Not sure how to read this")

    rpkg.header = Header(f)
    patch_offset = f.tell()

    if ((rpkg.version == 1 and file_size <= 0x14) or rpkg.version == 2 and file_size <= 0x1D):
        exit("Empty RPKG file?")

    # Determine if it's a patch file
    if (rpkg.version == 1 and rpkg.header.patch_count * 8 + 0x24 >= file_size):
        rpkg.is_patch_file = False
    elif (rpkg.version == 2 and rpkg.header.patch_count * 8 + 0x2D >= file_size):
        rpkg.is_patch_file = False
    else:
        if (rpkg.version == 1):
            f.seek(rpkg.header.patch_count * 8 + 0x1B)
        else:
            f.seek(rpkg.header.patch_count * 8 + 0x24)
        test_zero_value = int.from_bytes(f.read(1), 'little')
        test_header_offset = int.from_bytes(f.read(8), 'little')
        if (
            rpkg.version == 1 and 
            test_header_offset == (rpkg.header.hash_header_table_size + rpkg.header.hash_resource_table_size + rpkg.header.patch_count * 8 + 0x14)
            and test_zero_value == 0
        ):
            rpkg.is_patch_file = True
        elif (
            rpkg.version == 2 and 
            test_header_offset == (rpkg.header.hash_header_table_size + rpkg.header.hash_resource_table_size + rpkg.header.patch_count * 8 + 0x1D)
            and test_zero_value == 0
        ):
            rpkg.is_patch_file = True
        
    if (rpkg.is_patch_file):
        if (rpkg.header.patch_count > 0):
            f.seek(patch_offset)
            patch_entry_list: List[int] = []
            for _ in range(0, rpkg.header.patch_count):
                patch_entry_list.append(int.from_bytes(f.read(8), 'little'))
                # TODO: This doesn't appear to actually be used anywhere as of now
                # Given that we immediately seek to this point anyways, it's not
                # that we're progressing in the file...not sure why.

    # Seek to the hash data table's offset
    hash_data_offset = 0x10
    if (rpkg.version == 2):
        hash_data_offset += 9
    if (rpkg.is_patch_file):
        hash_data_offset += rpkg.header.patch_count * 8 + 4

    f.seek(hash_data_offset)

    for i in range(0, rpkg.header.hash_count):
        # Create a new hash
        hash = Hash(HashHeader(f))
        rpkg.hashes[i] = hash

    last_perc = 0.0
    for i in range(rpkg.header.hash_count):
        # Progress tracking
        new_perc = round(i * 100.0 / rpkg.header.hash_count, 1)
        if new_perc > last_perc:
            last_perc = new_perc
            print(str(new_perc) + '%' + ' - ' + str(i))

        rpkg.hashes[i].resource = HashResource(f)
        
        # Determine hash's size and if it is LZ4ed and/or XORed
        if (rpkg.hashes[i].header.data_size & 0x3FFFFFFF) != 0:
            rpkg.hashes[i].lz4ed = True
            rpkg.hashes[i].size = rpkg.hashes[i].header.data_size

            if (rpkg.hashes[i].header.data_size & 0x80000000) == 0x80000000:
                rpkg.hashes[i].size &= 0x3FFFFFFF
                rpkg.hashes[i].xored = True
        else:
            rpkg.hashes[i].size = rpkg.hashes[i].resource.size_final
            if (rpkg.hashes[i].header.data_size & 0x80000000) == 0x80000000:
                rpkg.hashes[i].xored = True
        
        rpkg.hashes[i].hash_value = rpkg.hashes[i].header.hash
        rpkg.hashes[i].hash_resource_type = rpkg.hashes[i].resource.resource_type

        if rpkg.hashes[i].resource.reference_table_size > 0:
            hash_reference_data = HashReferenceData(f)
            rpkg.hashes[i].hash_reference_data = hash_reference_data
            
        # Calculate from dependencies
        rpkg.hashes_by_hash[rpkg.hashes[i].hash_value] = rpkg.hashes[i]
        for dependency in rpkg.hashes[i].getDependencies():
            if dependency not in rpkg.reverse_dependencies:
                rpkg.reverse_dependencies[dependency] = []
            rpkg.reverse_dependencies[dependency].append(rpkg.hashes[i].hash_value)

        # Calculate hex string
        # Adapted from get_hash_in_rpkg_data_in_hex_view in 
        # https://github.com/glacier-modding/RPKG-Tool/blob/344f6a9c73abe41edfda427e17ed2aa4189fdb3e/rpkg_src/rpkg_dll.cpp#L825
        if rpkg.hashes[i].lz4ed:
            hash_size = rpkg.hashes[i].header.data_size
            if rpkg.hashes[i].xored:
                hash_size &= 0x3FFFFFFF
        else:
            hash_size = rpkg.hashes[i].resource.size_final

        f2 = open(rpkg_path, 'rb')
        f2.seek(rpkg.hashes[i].header.data_offset)
        raw_data = bytearray(f2.read(hash_size))
        f2.close()
        if rpkg.hashes[i].xored:
            raw_data = xor(raw_data, hash_size)

        if rpkg.hashes[i].lz4ed:
            data_size = rpkg.hashes[i].resource.size_final
            raw_data = decompress(raw_data, data_size)
        else:
            data_size = hash_size

        # RTLV, LOCR, DLGE are all JSON
        if rpkg.hashes[i].hash_resource_type == 'LOCR':
            locr = decode_locr_to_json_strings(raw_data)
            rpkg.hashes[i].hex_strings = flatten_locr_dict_to_set(locr)
            # LINE will use this later
            rpkg.hashes[i].data_dump = locr
        elif rpkg.hashes[i].hash_resource_type == 'DLGE':
            string = decode_dlge_to_string(raw_data)
            if string is not None:
                rpkg.hashes[i].hex_strings = [string]
        elif rpkg.hashes[i].hash_resource_type == 'LINE':
            # We can use LOCR data to convert this before writing to JSON in
            # the build_json.py file
            rpkg.hashes[i].data_dump = int.from_bytes(raw_data[0:4], 'little')
        # Just directly inline JSON
        elif rpkg.hashes[i].hash_resource_type == 'JSON':
            rpkg.hashes[i].hex_strings = [raw_data.decode('utf-8')]
        else:
            rpkg.hashes[i].hex_strings = chunkify_bytes(raw_data, data_size, rpkg.hashes[i].hash_resource_type)

    f.close()
    return rpkg
