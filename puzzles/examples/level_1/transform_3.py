def hidden_transform(data: bytes) -> bytes:
    # XOR then add
    return bytes([(b ^ 0xAF + 15) % 256 for b in data])