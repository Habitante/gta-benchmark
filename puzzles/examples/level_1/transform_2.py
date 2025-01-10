def hidden_transform(data: bytes) -> bytes:
    # Simple AND then addition (introduces AND)
    return bytes([((b & 0xF5) + 0x0B) % 256 for b in data])