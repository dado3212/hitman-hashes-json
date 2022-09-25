from typing import BinaryIO, Dict, List
from Hash import Hash

# Adapted from rpkg_src/rpkg.h

class Header:
    def __init__(self, f: BinaryIO):
        self.hash_count = int.from_bytes(f.read(4), 'little')
        self.hash_header_table_size = int.from_bytes(f.read(4), 'little')
        self.hash_resource_table_size = int.from_bytes(f.read(4), 'little')
        self.patch_count = int.from_bytes(f.read(4), 'little')

class RPKG:
    version: int = -1
    # Only used in version 2
    v2_header: bytes
    is_patch_file: bool = False

    header: Header
    hashes: Dict[int, Hash] = dict()
    hashes_by_hash: Dict[int, Hash] = dict()
    reverse_dependencies: Dict[int, List[int]] = dict()

    def __init__(self, file_name: str, file_path: str):
        self.file_name = file_name
        self.file_path = file_path

    