def hidden_transform(data: bytes) -> bytes:
    # Single XOR (simplest bitwise op)
    return bytes([b ^ 0xA5 for b in data])