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
    def __init__(self, file_name: str, file_path: str):
        self.file_name = file_name
        self.file_path = file_path

        self.version: int = -1
        # Only used in version 2
        self.v2_header: bytes
        self.is_patch_file: bool = False

        self.header: Header
        self.hashes: Dict[int, Hash] = dict()
        self.hashes_by_hash: Dict[int, Hash] = dict()
        self.reverse_dependencies: Dict[int, List[int]] = dict()

    