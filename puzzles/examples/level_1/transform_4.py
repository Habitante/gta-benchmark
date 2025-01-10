def hidden_transform(data: bytes) -> bytes:
    # Conditional transform (introduces branching)
    return bytes([b ^ 0x55 if b & 0x40 else b ^ 0xAA for b in data])