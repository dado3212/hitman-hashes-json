import hashlib

def hash_to_hex(hash: int) -> str:
    return format(hash, 'x').upper().rjust(16, '0')

def hex_to_hash(hex: str) -> int:
    return int(hex.lstrip('0'), 16)

def ioi_string_to_hex(path: str) -> str:
    raw = hashlib.md5(path.encode()).hexdigest().upper()
    return '00' + raw[2:16]

def print_bytes(raw_bytes: bytes) -> None:
    count = 0
    string = ''
    for i in raw_bytes:
        if count % 16 == 0:
            print(string)
            string = ''
        string += hex(i)[2:].zfill(2).upper() + ' '
        count += 1
    print(string)