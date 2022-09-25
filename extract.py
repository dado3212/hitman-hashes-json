from os.path import getsize
from typing import List
from Hash import Hash, HashHeader, HashResource, HashReferenceData
from RPKG import RPKG, Header

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

    for i in range(rpkg.header.hash_count):
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
            
        rpkg.hashes_by_hash[rpkg.hashes[i].hash_value] = rpkg.hashes[i]
        for dependency in rpkg.hashes[i].getDependencies():
            if dependency not in rpkg.reverse_dependencies:
                rpkg.reverse_dependencies[dependency] = []
            rpkg.reverse_dependencies[dependency].append(rpkg.hashes[i].hash_value)

    f.close()
    return rpkg
