from typing import BinaryIO, List, Optional

class HashReferenceData:
    def __init__(self, f: BinaryIO):
        depends_count = int.from_bytes(f.read(4), 'little')
        self.hash_reference_count = depends_count
        depends_count &= 0x3FFFFFFF
        
        self.hash_reference_type: List[int] = []
        for _ in range(depends_count):
            self.hash_reference_type.append(int.from_bytes(f.read(1), 'little'))

        self.hash_reference: List[int] = []
        for _ in range(depends_count):
            self.hash_reference.append(int.from_bytes(f.read(8), 'little'))

class HashHeader:
    def __init__(self, f: BinaryIO):
        self.hash = int.from_bytes(f.read(8), 'little')
        self.data_offset = int.from_bytes(f.read(8), 'little')
        self.data_size = int.from_bytes(f.read(4), 'little')

class HashResource:
    def __init__(self, f: BinaryIO):
        resource_type_bytes: List[bytes] = []
        for _ in range(4):
            resource_type_bytes.append(f.read(1))
        self.resource_type = "".join([x.decode("utf-8") for x in resource_type_bytes[::-1]])
        self.reference_table_size = int.from_bytes(f.read(4), 'little')
        self.reference_table_dummy = int.from_bytes(f.read(4), 'little')
        self.size_final = int.from_bytes(f.read(4), 'little')
        self.size_in_memory = int.from_bytes(f.read(4), 'little')
        self.size_in_video_memory = int.from_bytes(f.read(4), 'little')

class Hash:
    def __init__(self, header: HashHeader):
        self.header = header

        self.header: HashHeader
        self.resource: HashResource
        self.hash_reference_data: Optional[HashReferenceData] = None

        self.lz4ed: bool = False
        self.xored: bool = False
        self.size: int = 0
        # TODO: This is a duplicate of self.header.hash
        self.hash_value: int = 0
        self.hash_resource_type: str = ''

        self.chunks: List[str] = []

    def getHexName(self) -> str:
        return self.getFormattedHash() + '.' + self.hash_resource_type

    def getFormattedHash(self) -> str:
        main = format(self.hash_value, 'x').upper()
        return main.rjust(16, '0')

    def getDependencies(self) -> List[int]:
        reference_data = self.hash_reference_data
        if reference_data is None:
            return []
        else:
            return reference_data.hash_reference
