from pbkdf2 import PBKDF2
from Cryptodome.Cipher import AES
from enum import IntEnum


class XorShift:
    def __init__(
            self,
            seed: int
    ):
        self.seed = seed
        self.y = seed

    def next(self) -> int:
        v3: int = self.y ^ ((self.y << 13) & 0xffffffff)
        v4: int = v3 ^ (v3 >> 17) ^ (32 * (v3 ^ (v3 >> 17))) & 0xffffffff
        self.y = v4

        return v4

    def make_swizzle_table(
            self,
            source: bytearray
    ):
        if len(source) >= 1:
            v4: int = 0
            v5: int = len(source)

            while True:
                result: int = self.next()
                source[v4] = (result >> 3) & 0xFF
                v4 = v4 + 1

                if v5 == v4:
                    break


class LightWeightEncryptor:
    def __init__(
            self,
            seed: int,
            init_spin: int,
            table_size: int
    ):
        self.shifter = XorShift(seed)
        if init_spin >= 1:
            while True:
                self.shifter.next()
                init_spin = init_spin - 1

                if init_spin <= 0:
                    break

        self.swizzle_bytes: bytearray = bytearray(table_size)
        self.shifter.make_swizzle_table(self.swizzle_bytes)
        self.coef = (self.shifter.next() & 0xF) + 3
        self.offset = (self.shifter.next() & 0x1F) + 1

    def modify(
            self,
            source: bytearray,
            offset: int,
            count: int,
            stream_offset: int,
            salt: int
    ):
        v13: int = 0
        v14: int = len(self.swizzle_bytes) - 1

        while True:
            v18: int = source[offset + v13]
            v20 = (self.offset + (stream_offset + offset + salt + v13) * self.coef) & v14
            if v20 >= len(self.swizzle_bytes):
                raise IndexError

            source[offset + v13] = self.swizzle_bytes[v20] ^ v18
            v13 = v13 + 1

            if count == v13:
                break

    def transform(
            self,
            input_bytes: bytearray,
            input_offset: int,
            input_count: int
    ):
        raise NotImplementedError


class RijndaelEncryptor:
    def __init__(self, pw: str, salt: str, decrypt: bool):
        self.pw = pw.encode("UTF-8")
        self.salt = salt.encode("UTF-8")
        self.decrypt = decrypt

        self.rfc2898 = PBKDF2(self.pw, self.salt, iterations=117)

        self.key = self.rfc2898.read(16)
        self.iv = self.rfc2898.read(16)
        self.rijndael = AES.new(self.key, AES.MODE_CBC, self.iv)

        self.transform_method = self.rijndael.decrypt if decrypt else self.rijndael.encrypt

    def modify(
            self,
            source: bytearray,
            offset: int,
            count: int,
            stream_offset: int,
            salt: int
    ):
        raise NotImplementedError

    def transform(
            self,
            input_bytes: bytearray,
            input_offset: int,
            input_count: int
    ):

        return self.transform_method(input_bytes)


class Keys(IntEnum):

    EMBEDED_AES_KEY = 1001
    EMBEDED_ASSETBUNDLE_KEY = 1002
    EMBEDED_DAT_KEY = 1003
    EMBEDED_FILELIST_KEY = 1004
    DEFAULT_KEY = 1501
    DOWNLOAD_ASSETBUNDLE_KEY_1 = 2001
    DOWNLOAD_DAT_KEY = 2002
    DOWNLOAD_DB_KEY = 2003


Encryptors = {
    1001: RijndaelEncryptor('Pg97xygbey7aw', '857fesfd', True),
    1002: LightWeightEncryptor(1749853741, 11, 512),
    1003: LightWeightEncryptor(0xCE2B9A93, 13, 512),
    1004: LightWeightEncryptor(874156713, 17, 512),
    1501: RijndaelEncryptor('CgU6T5tehiGoZ', '37F741ED', True),
    2001: LightWeightEncryptor(0x51C1D53, 17, 512),
    2002: LightWeightEncryptor(0xF5F1B55, 13, 512),
    2003: LightWeightEncryptor(0x28087953, 11, 512),
}

