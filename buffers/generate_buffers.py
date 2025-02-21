# buffers/generate_buffers.py

import random


def generate_visible_buffers():
    """
    Generate 24 visible test buffers of 64 bytes each, carefully structured
    to help understand transformations.
    """
    buffers = []

    # 1-2) Uniform buffers (0x00 and 0xFF)
    buffers.append(bytes([0x00] * 64))
    buffers.append(bytes([0xFF] * 64))

    # 3-6) Single-byte variations in all-zero buffer
    single_variations_zero = [0x01, 0x02, 0x80, 0xAA]
    for val in single_variations_zero:
        buf = bytearray([0x00] * 64)
        buf[0] = val  # Always at start for easier pattern spotting
        buffers.append(bytes(buf))

    # 7-10) Single-byte variations in all-FF buffer
    single_variations_ff = [0x00, 0xF0, 0x0F, 0x55]
    for val in single_variations_ff:
        buf = bytearray([0xFF] * 64)
        buf[0] = val
        buffers.append(bytes(buf))

    # 11-12) Sequential patterns
    buffers.append(bytes(range(64)))  # 0x00 to 0x3F
    buffers.append(bytes(range(255, 191, -1)))  # 0xFF to 0xC0

    # 13-14) Alternating patterns
    buffers.append(bytes([0xAA, 0x55] * 32))
    buffers.append(bytes([0x55, 0xAA] * 32))

    # 15-16) Bit patterns
    buffers.append(bytes([0xF0] * 64))
    buffers.append(bytes([0x0F] * 64))

    # 17) Powers of 2 in 8-byte chunks
    pow2_chunks = bytearray(64)
    for i in range(8):
        chunk_val = 1 << i  # 1, 2, 4, 8, 16, 32, 64, 128
        pow2_chunks[i*8:(i+1)*8] = [chunk_val] * 8
    buffers.append(bytes(pow2_chunks))

    # Powers of 2 and offset variants (8 bytes chunks, 8 chunks = 64 bytes)
    pattern_test = bytearray(64)
    for i in range(8):  # 8 chunks
        base = 1 << (i % 4)  # 1, 2, 4, 8 repeating pattern
        # Fill first half of chunk with base value
        chunk_start = i * 8
        chunk_mid = chunk_start + 4
        chunk_end = chunk_start + 8
        pattern_test[chunk_start:chunk_mid] = [base] * 4
        # Fill second half with base+1
        pattern_test[chunk_mid:chunk_end] = [base + 1] * 4
    buffers.append(bytes(pattern_test))

    # 19) Rolling single bit + complement
    bit_patterns = bytearray(64)
    for i in range(64):
        if i < 32:
            bit_patterns[i] = 1 << (i % 8)  # Single bit set
        else:
            bit_patterns[i] = (1 << (i % 8)) ^ 0xFF  # Single bit clear
    buffers.append(bytes(bit_patterns))

    # 20) ASCII text repeated
    text = "Hello, World! "
    buffers.append((text * 5)[:64].encode('ascii'))

    # 21) ASCII text repeated
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do "
    buffers.append((text * 5)[:64].encode('ascii'))

    # 22) Fibonacci sequence mod 256
    fib = bytearray(64)
    fib[0], fib[1] = 1, 1
    for i in range(2, 64):
        fib[i] = (fib[i-1] + fib[i-2]) % 256
    buffers.append(bytes(fib))

    # 23) Random but reproducible
    random.seed(4)  # Fixed seed for reproducibility
    buffers.append(bytes([random.randint(0, 255) for _ in range(64)]))

    # 24) Random but reproducible
    random.seed(0)  # Fixed seed for reproducibility
    buffers.append(bytes([random.randint(0, 255) for _ in range(64)]))

    return buffers

def get_missing_bytes(visible_buffers):
    """
    Calculate missing byte values from visible buffers.
    """
    seen_bytes = set()
    for buf in visible_buffers:
        seen_bytes.update(buf)
    return set(range(256)) - seen_bytes

def generate_hidden_buffers(missing_bytes):
    """
    Generate 24 hidden validation buffers, ensuring each contains missing bytes.
    """
    random.seed(1337)  # Different seed for hidden buffers
    buffers = []
    missing_bytes_list = list(missing_bytes)  # Convert set to list for random.choice

    # 1-4) More complex patterns
    buffers.append(bytes([x ^ (x >> 4) for x in range(64)]))  # XOR pattern
    buffers.append(bytes([(x * 7 + 13) % 256 for x in range(64)]))  # Linear transform
    buffers.append(bytes([pow(x, 2, 256) for x in range(64)]))  # Square numbers
    buffers.append(bytes([pow(3, x, 256) for x in range(64)]))  # Powers of 3

    # 5-8) Mixed patterns
    for _ in range(4):
        buf = bytearray(64)
        pattern_length = random.randint(2, 8)
        # Ensure at least one missing byte in each pattern
        pattern = [random.choice(list(missing_bytes))] + [random.randint(0, 255) for _ in range(pattern_length - 1)]
        for i in range(64):
            buf[i] = pattern[i % pattern_length]
        buffers.append(bytes(buf))

    # 9-12) Structured random with guaranteed missing bytes
    for _ in range(4):
        buf = bytearray(64)
        missing_byte = random.choice(list(missing_bytes))
        for i in range(64):
            if i % 8 == 0:  # Insert missing byte every 8 positions
                buf[i] = missing_byte
            else:
                buf[i] = (i * random.randint(1, 7) + random.randint(0, 255)) % 256
        buffers.append(bytes(buf))

    # 13-16) More text patterns with different encodings
    texts = ["Test 123!", "Python<>", "0xCAFE :)", "Binary..."]
    for text in texts:
        buf = bytearray(64)
        encoded = text.encode('utf-8')
        buf[:len(encoded)] = encoded
        # Fill rest with some missing bytes
        for i in range(len(encoded), 64):
            if i % 8 == 0:
                buf[i] = random.choice(list(missing_bytes))
            else:
                buf[i] = random.randint(0, 255)
        buffers.append(bytes(buf))

    # 17-24) Pure random buffers with guaranteed missing bytes
    for _ in range(8):  # Increased to 8 buffers
        buf = bytearray(64)
        missing_byte = random.choice(list(missing_bytes))
        for i in range(64):
            if i % 16 == 0:  # Insert missing byte every 16 positions
                buf[i] = missing_byte
            else:
                buf[i] = random.randint(0, 255)
        buffers.append(bytes(buf))

    # Add missing bytes at strategic positions in remaining buffers
    for buf in buffers:
        # Modify first byte if no missing bytes present
        if not any(b in missing_bytes for b in buf):
            new_buf = bytearray(buf)
            new_buf[0] = random.choice(missing_bytes_list)
            buffers[buffers.index(buf)] = bytes(new_buf)

    return buffers


def save_buffers(buffers, prefix, directory='shared'):
    """
    Save buffers with given prefix (visible/hidden).
    """
    os.makedirs(directory, exist_ok=True)
    for idx, buf in enumerate(buffers, start=1):
        filename = os.path.join(directory, f'{prefix}_{idx:02d}.bin')
        with open(filename, 'wb') as f:
            f.write(buf)
    print(f"Saved {len(buffers)} {prefix} buffers to '{directory}/'.")


def generate_puzzle_prompt_header():
    """
    Generates the standardized first part of the puzzle prompt, including all visible input buffers.
    Returns both the text and the visible buffers for later use.
    """
    visible_buffers = generate_visible_buffers()

    prompt = """Below is a puzzle involving 24 input buffers and their transformed outputs.
Each buffer is exactly 64 bytes, shown in hex.

Your task: Figure out the logic of the transformation used to go from the INPUT to the OUTPUT.
Then, provide a Python function that, given any new 64-byte buffer, will produce the correct transformed output.

Here are the 24 input (SRC) buffers in hex (one line per buffer):
"""

    # Add each input buffer to the prompt
    for i, buf in enumerate(visible_buffers, 1):
        hex_str = buf.hex()
        prompt += f"INPUT #{i:02d}: {hex_str}\n"

    # Note: We don't add outputs here as they'll be different for each transform
    return prompt, visible_buffers


if __name__ == "__main__":
    import os

    # Generate and save buffers
    prompt_header, visible_buffers = generate_puzzle_prompt_header()
    # Calculate missing bytes
    missing_bytes = get_missing_bytes(visible_buffers)
    print(f"Total unique bytes in visible inputs: {256 - len(missing_bytes)}")
    print(f"Number of missing bytes in visible inputs: {len(missing_bytes)}")
    print("Missing byte values on input buffers: ")
    print([f"0x{x:02X}" for x in sorted(list(missing_bytes))])
    # Generate hidden buffers with missing bytes information
    hidden_buffers = generate_hidden_buffers(missing_bytes)

    # Save the prompt header for later use
    with open('shared/prompt_header.txt', 'w') as f:
        f.write(prompt_header)

    # Save the buffers
    save_buffers(visible_buffers, 'visible')
    save_buffers(hidden_buffers, 'hidden')

    print("Generated prompt header and saved to 'buffers/shared/prompt_header.txt'")