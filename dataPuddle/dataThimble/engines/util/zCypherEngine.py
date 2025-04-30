# Last modified: 2025-03-31 15:04:34
# Version: 0.0.1
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def base62_encode(n: int) -> str:
    if n == 0:
        return ALPHABET[0]
    s = ""
    while n > 0:
        n, r = divmod(n, 62)
        s = ALPHABET[r] + s
    return s


def base62_decode(s: str) -> int:
    n = 0
    for c in s:
        n = n * 62 + ALPHABET.index(c)
    return n


def encode_string(s: str) -> str:
    b = s.encode("utf-8")
    i = int.from_bytes(b, byteorder="big")
    return base62_encode(i)


def decode_string(encoded: str) -> str:
    i = base62_decode(encoded)
    b_len = (i.bit_length() + 7) // 8  # how many bytes needed
    b = i.to_bytes(b_len, byteorder="big")
    return b.decode("utf-8")
