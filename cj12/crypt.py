import numpy as np

class AES:
    """
    Perform AES-128, -192 or -256 encryption and decryption.

    Usage:
    ```
    aes = AES(key: bytes)  # sets up an AES encryptor/decryptor object using key
    ```
    """
    # Set up S-box
    sbox = np.array([
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    ], dtype=np.uint8)

    # Set up inverse S-box for decryption
    sbox_inv = np.empty(shape=sbox.shape, dtype=np.uint8)
    for i in range(len(sbox)):
        sbox_inv[sbox[i]] = i

    Rcon = np.array([
        [0x01, 0x00, 0x00, 0x00], [0x02, 0x00, 0x00, 0x00], [0x04, 0x00, 0x00, 0x00], [0x08, 0x00, 0x00, 0x00], [0x10, 0x00, 0x00, 0x00],
        [0x20, 0x00, 0x00, 0x00], [0x40, 0x00, 0x00, 0x00], [0x80, 0x00, 0x00, 0x00], [0x1B, 0x00, 0x00, 0x00], [0x36, 0x00, 0x00, 0x00]
    ], dtype=np.uint8)

    shift_idx = np.array([[0, 1, 2, 3],   # first row unshifted
                          [1, 2, 3, 0],   # second row rolled left by 1
                          [2, 3, 0, 1],   # third row rolled left by 2
                          [3, 0, 1, 2]])  # last row rolled left by 3

    unshift_idx = np.array([[0, 1, 2, 3],
                            [3, 0, 1, 2],
                            [2, 3, 0, 1],
                            [1, 2, 3, 0]])


    @staticmethod
    def sub_bytes(arr: np.ndarray, sbox) -> np.ndarray:
        return sbox[arr]


    @staticmethod
    def mul2(x: int) -> int:
        result = (x << 1) & 0xFF
        if x & 0x80: result ^= 0x1B
        return result


    @staticmethod
    def mix_column(col: np.ndarray) -> np.ndarray:
        x2 = AES.mul2
        c0 = x2(col[0]) ^ (x2(col[1]) ^ col[1]) ^ col[2] ^ col[3]
        c1 = col[0] ^ x2(col[1]) ^ (x2(col[2]) ^ col[2]) ^ col[3]
        c2 = col[0] ^ col[1] ^ x2(col[2]) ^ x2(col[3]) ^ col[3]
        c3 = x2(col[0]) ^ col[0] ^ col[1] ^ col[2] ^ x2(col[3])
        return np.array([c0, c1 ,c2, c3], dtype=np.uint8)


    @staticmethod
    def mix_columns(grid: np.ndarray) -> None:
        for col in range(4):
            grid[:, col] = AES.mix_column(grid[:, col])


    @staticmethod
    def unmix_column(col: np.ndarray) -> np.ndarray:
        x2 = AES.mul2
        c02 = x2(col[0]); c04 = x2(c02); c08 = x2(c04)
        c12 = x2(col[1]); c14 = x2(c12); c18 = x2(c14)
        c22 = x2(col[2]); c24 = x2(c22); c28 = x2(c24)
        c32 = x2(col[3]); c34 = x2(c32); c38 = x2(c34)
        c0 = (c08 ^ c04 ^ c02) ^ (c18 ^ c12 ^ col[1]) ^ (c28 ^ c24 ^ col[2]) ^ (c38 ^ col[3])  # [14, 11, 13, 9]
        c1 = (c08 ^ col[0]) ^ (c18 ^ c14 ^ c12) ^ (c28 ^ c22 ^ col[2]) ^ (c38 ^ c34 ^ col[3])  # [9, 14, 11, 13]
        c2 = (c08 ^ c04 ^ col[0]) ^ (c18 ^ col[1]) ^ (c28 ^ c24 ^ c22) ^ (c38 ^ c32 ^ col[3])    # [13, 9, 14, 11]
        c3 = (c08 ^ c02 ^ col[0]) ^ (c18 ^ c14 ^ col[1]) ^ (c28 ^ col[2]) ^ (c38 ^ c34 ^ c32)    # [11, 13, 9, 14]
        return np.array([c0, c1 ,c2, c3], dtype=np.uint8)


    @staticmethod
    def unmix_columns(grid: np.ndarray) -> None:
        for col in range(4):
            grid[:, col] = AES.unmix_column(grid[:, col])


    @staticmethod
    def shift_rows(arr: np.ndarray, shifter) -> None:
        arr[:] = arr[:, np.arange(4).reshape(4, 1), shifter]


    def __init__(self, key: bytes):
        if len(key) * 8 not in [128, 192, 256]:
            raise ValueError("Key has an incorrect number of bits! (Should be 128, 192, or 256-bit)")
        self.key = np.frombuffer(key, dtype=np.uint8)
        self.Nk = len(self.key) // 4  # No. of 32-bit words in `key`
        self.Nr = self.Nk + 6         # No. of encryption rounds
        self.Nb = 4                   # No. of words in AES state
        self.round_keys = self._key_expansion()


    def _key_expansion(self) -> np.ndarray:
        words = np.empty((self.Nb * (self.Nr + 1) * 4, ), dtype=np.uint8)
        words[:len(self.key)] = self.key
        words = words.reshape(-1, 4)
        rcon_iter = iter(AES.Rcon)
        for i in range(self.Nk, len(words)):
            if i % self.Nk == 0:
                words[i] = AES.sub_bytes(np.roll(words[i-1], -1), AES.sbox) ^ next(rcon_iter) ^ words[i-4]
            elif self.Nk == 8 and i % self.Nk == 4:
                words[i] = AES.sub_bytes(words[i-1], AES.sbox) ^ words[i-4]
            else:
                words[i] = words[i-1] ^ words[i-4]
        return words.reshape(-1, 4, 4).transpose(0, 2, 1)


    def encrypt(self, data: bytes) -> bytes:
        pad_length = 16 - len(data) % 16
        padded = np.concat((np.frombuffer(data, dtype=np.uint8), np.full(pad_length, pad_length))).reshape(-1, 4, 4).transpose(0, 2, 1)
        self.debug_print(padded)
        keys_iter = iter(self.round_keys)

        # Pre-round: add round key
        padded ^= next(keys_iter)
        self.debug_print(padded)

        for round in range(self.Nr):
            padded = AES.sub_bytes(padded, AES.sbox)
            self.debug_print(padded)
            AES.shift_rows(padded, AES.shift_idx)
            self.debug_print(padded)
            if round != self.Nr - 1:
                for grid in padded:
                    AES.mix_columns(grid)
            self.debug_print(padded)
            padded ^= next(keys_iter)
            self.debug_print(padded)

        return padded.transpose(0, 2, 1).tobytes()


    def decrypt(self, data: bytes) -> bytes:
        encrypted = np.frombuffer(data, dtype=np.uint8).reshape(-1, 4, 4).transpose(0, 2, 1).copy()
        self.debug_print(encrypted)
        keys_iter = reversed(self.round_keys)

        # Pre-round: add round key
        encrypted ^= next(keys_iter)
        self.debug_print(encrypted)

        for round in range(self.Nr):
            if round != 0:
                for grid in encrypted:
                    AES.unmix_columns(grid)
            self.debug_print(encrypted)
            AES.shift_rows(encrypted, AES.unshift_idx)
            self.debug_print(encrypted)
            encrypted = AES.sub_bytes(encrypted, AES.sbox_inv)
            self.debug_print(encrypted)
            encrypted ^= next(keys_iter)
            self.debug_print(encrypted)

        encrypted = encrypted.transpose(0, 2, 1).tobytes()
        return encrypted[:-encrypted[-1]]


    def debug_print(self, arr):
        return
        for elem in arr.reshape(-1):
            print(f"{elem:02x} ", end='')
        print()


if __name__ == '__main__':
    # aes = AES(bytes([0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c]))
    # encrypted = aes.encrypt(bytes([0x32, 0x43, 0xf6, 0xa8, 0x88, 0x5a, 0x30, 0x8d, 0x31, 0x31, 0x98, 0xa2, 0xe0, 0x37, 0x07, 0x34]))
    # decrypted = aes.decrypt(encrypted)
    # print(decrypted)
    data = b"Hello, world!"
    key = b"1234567812345678"
    aes = AES(key)
    encrypted = aes.encrypt(data)
    print(encrypted)
    decrypted = aes.decrypt(encrypted)
    print(decrypted)