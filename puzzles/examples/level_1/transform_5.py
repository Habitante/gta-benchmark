def hidden_transform(data: bytes) -> bytes:
    # Multiple ops combining previous concepts
    return bytes([(((b << 3) & 0xEF) + 0x13) % 256 ^ (b >> 4) for b in data])
