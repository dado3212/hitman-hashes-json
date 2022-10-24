import unittest
from utils import hex_to_hash, hash_to_hex, ioi_string_to_hex
from extract import chunkify_bytes

class UtilsTest(unittest.TestCase):

    def test_hex_to_hash(self):
        self.assertEqual(hex_to_hash('0023432D2C4E9603'), 9925485480809987)
        self.assertEqual(hex_to_hash('0015166FD329DF6C'), 5935644050841452)

    def test_hash_to_hex(self):
        self.assertEqual(hash_to_hex(9925485480809987), '0023432D2C4E9603')
        self.assertEqual(hash_to_hex(5935644050841452), '0015166FD329DF6C')

    def test_ioi_string_to_hex(self):
        self.assertEqual(ioi_string_to_hex('[assembly:/_pro/environment/textures/constants/color_black.texture?/diffuse_a.tex](ascolormap).pc_tex'), '006BC76DF396C49E')
        self.assertEqual(ioi_string_to_hex('[[assembly:/_pro/environment/materialclasses/basicmaterial.materialclass].fx](dx11).pc_mate'), '00E7D648A187A9C1')

    def test_chunkify_bytes(self):
        string = 'hello~there'
        byte = [ord(x) if x != '~' else 12 for x in string]
        self.assertEqual(chunkify_bytes(bytearray(byte), len(string), 5), ['hello', 'there'])
        string = 'Testing~thisone~out~'
        byte = [ord(x) if x != '~' else 12 for x in string]
        self.assertEqual(chunkify_bytes(bytearray(byte), len(string), 5), ['Testing', 'thisone'])
        string = '~h~~e~llothere~~12'
        byte = [ord(x) if x != '~' else 12 for x in string]
        self.assertEqual(chunkify_bytes(bytearray(byte), len(string), 5), ['llothere'])

if __name__ == '__main__':
    unittest.main()