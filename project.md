# Project Documentation

This document contains the structure of the project and the source code for each file.

## Project Structure

```

- `app.py`
- `gta_benchmark.md`
- `main.py`
- `puzzle_bench.db`
- `requirements.txt`
- `sandbox.py`
- **buffers/**
  - `generate_buffers.py`
  - **shared/**
    - `hidden_01.bin`
    - `hidden_02.bin`
    - `hidden_03.bin`
    - `hidden_04.bin`
    - `hidden_05.bin`
    - `hidden_06.bin`
    - `hidden_07.bin`
    - `hidden_08.bin`
    - `hidden_09.bin`
    - `hidden_10.bin`
    - `hidden_11.bin`
    - `hidden_12.bin`
    - `hidden_13.bin`
    - `hidden_14.bin`
    - `hidden_15.bin`
    - `hidden_16.bin`
    - `hidden_17.bin`
    - `hidden_18.bin`
    - `hidden_19.bin`
    - `hidden_20.bin`
    - `prompt_header.txt`
    - `visible_01.bin`
    - `visible_02.bin`
    - `visible_03.bin`
    - `visible_04.bin`
    - `visible_05.bin`
    - `visible_06.bin`
    - `visible_07.bin`
    - `visible_08.bin`
    - `visible_09.bin`
    - `visible_10.bin`
    - `visible_11.bin`
    - `visible_12.bin`
    - `visible_13.bin`
    - `visible_14.bin`
    - `visible_15.bin`
    - `visible_16.bin`
    - `visible_17.bin`
    - `visible_18.bin`
    - `visible_19.bin`
    - `visible_20.bin`
- **puzzles/**
  - **benchmark/**
    - `readme.md`
    - **level_1/**
      - `hidden_outputs_1.bin`
      - `hidden_outputs_2.bin`
      - `hidden_outputs_3.bin`
      - `hidden_outputs_4.bin`
      - `hidden_outputs_5.bin`
      - `prompt_1.txt`
      - `prompt_2.txt`
      - `prompt_3.txt`
      - `prompt_4.txt`
      - `prompt_5.txt`
      - `transform_1.py`
      - `transform_2.py`
      - `transform_3.py`
      - `transform_4.py`
      - `transform_5.py`
      - `visible_outputs_1.bin`
      - `visible_outputs_2.bin`
      - `visible_outputs_3.bin`
      - `visible_outputs_4.bin`
      - `visible_outputs_5.bin`
    - **level_2/**
      - `hidden_outputs_1.bin`
      - `hidden_outputs_2.bin`
      - `hidden_outputs_3.bin`
      - `hidden_outputs_4.bin`
      - `hidden_outputs_5.bin`
      - `prompt_1.txt`
      - `prompt_2.txt`
      - `prompt_3.txt`
      - `prompt_4.txt`
      - `prompt_5.txt`
      - `transform_1.py`
      - `transform_2.py`
      - `transform_3.py`
      - `transform_4.py`
      - `transform_5.py`
      - `visible_outputs_1.bin`
      - `visible_outputs_2.bin`
      - `visible_outputs_3.bin`
      - `visible_outputs_4.bin`
      - `visible_outputs_5.bin`
  - **examples/**
    - **level_1/**
      - `hidden_outputs_1.bin`
      - `hidden_outputs_2.bin`
      - `hidden_outputs_3.bin`
      - `hidden_outputs_4.bin`
      - `hidden_outputs_5.bin`
      - `prompt_1.txt`
      - `prompt_2.txt`
      - `prompt_3.txt`
      - `prompt_4.txt`
      - `prompt_5.txt`
      - `transform_1.py`
      - `transform_2.py`
      - `transform_3.py`
      - `transform_4.py`
      - `transform_5.py`
      - `visible_outputs_1.bin`
      - `visible_outputs_2.bin`
      - `visible_outputs_3.bin`
      - `visible_outputs_4.bin`
      - `visible_outputs_5.bin`
- **scripts/**
  - `apply_transforms.py`
- **submissions/**
- **templates/**
  - `index.html`
  - `puzzle.html`

```

## Source Code

### `app.py`

```python

# app.py
from pathlib import Path
from sandbox import DockerSandbox
from flask import Flask, request, jsonify, render_template
from datetime import datetime
import docker
import tempfile
import sqlite3
import os

app = Flask(__name__)

docker_sandbox = DockerSandbox()

# Initialize SQLite database
def init_db():
    with sqlite3.connect('puzzle_bench.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS submissions
                    (id INTEGER PRIMARY KEY,
                     puzzle_id TEXT,
                     user_name TEXT,
                     total_score REAL,
                     visible_score REAL,
                     hidden_score REAL,
                     execution_time REAL,
                     code_length INTEGER,
                     timestamp DATETIME)''')
        conn.commit()

# Puzzle metadata structure
PUZZLE_METADATA = {
    1: {
        'name': 'Single Byte - Basic',
        'description': 'Basic transformations on individual bytes',
        'complexity': {
            'window': '1 byte',
            'operations': '1-3 ops per byte',
            'state': 'none'
        }
    },
    2: {
        'name': 'Single Byte - Advanced',
        'description': 'Complex transformations on individual bytes',
        'complexity': {
            'window': '1 byte',
            'operations': '3-6 ops per byte',
            'state': 'none',
            'features': 'conditionals, bit manipulation'
        }
    },
    3: {
        'name': 'Byte Pairs',
        'description': 'Operations on adjacent byte pairs',
        'complexity': {
            'window': '2 bytes',
            'operations': '1-2 ops per window',
            'state': 'none'
        }
    },
    4: {
        'name': 'Byte Pairs - Advanced',
        'description': 'Complex operations on byte pairs',
        'complexity': {
            'window': '2 bytes',
            'operations': '2-4 ops per window',
            'state': 'none'
        }
    },
    5: {
        'name': '4-Byte Blocks',
        'description': 'Operations on 4-byte blocks',
        'complexity': {
            'window': '4 bytes',
            'operations': '1-3 ops per window',
            'state': 'none'
        }
    },
    6: {
        'name': '8-Byte Blocks',
        'description': 'Operations on 8-byte blocks',
        'complexity': {
            'window': '8 bytes',
            'operations': '1-3 ops per window',
            'state': 'none'
        }
    },
    7: {
        'name': 'Simple State',
        'description': 'Previous byte affects current transformation',
        'complexity': {
            'window': '1-2 bytes',
            'operations': '2-3 ops per byte',
            'state': 'previous byte only'
        }
    },
    8: {
        'name': 'Running State',
        'description': 'Accumulating state affects transformation',
        'complexity': {
            'window': '1 byte',
            'operations': '2-4 ops per byte',
            'state': 'running accumulator'
        }
    },
    9: {
        'name': 'Position Dependent',
        'description': 'Transformation varies by byte position',
        'complexity': {
            'window': '1 byte',
            'operations': '2-4 ops per byte',
            'state': 'position based'
        }
    },
    10: {
        'name': 'Multi-Pass',
        'description': 'Multiple passes through the data',
        'complexity': {
            'window': '1 byte',
            'operations': '1-3 ops per pass',
            'passes': '2-3',
            'state': 'running state between passes'
        }
    }
}


def get_available_puzzles():
    """
    Scan puzzle directory and combine with metadata.
    Returns dict of available puzzles with source and level grouping.
    """
    puzzles = {
        'benchmark': {},  # Will hold benchmark puzzles by level
        'examples': {}  # Will hold example puzzles by level
    }
    base_dir = 'puzzles'

    # Try benchmark first, then examples
    puzzle_dirs = ['benchmark', 'examples']

    for dir_name in puzzle_dirs:
        puzzles_dir = os.path.join(base_dir, dir_name)
        if not os.path.exists(puzzles_dir):
            continue

        for level_dir in os.listdir(puzzles_dir):
            if not level_dir.startswith('level_'):
                continue

            level_num = int(level_dir.split('_')[1])
            if level_num not in PUZZLE_METADATA:
                continue

            level_path = os.path.join(puzzles_dir, level_dir)
            if not os.path.isdir(level_path):
                continue

            # Find all transform files in this level
            transforms = [f for f in os.listdir(level_path)
                          if f.startswith('transform_') and f.endswith('.py')]

            if transforms:  # Only add level if it has transforms
                if level_num not in puzzles[dir_name]:
                    puzzles[dir_name][level_num] = []

                for transform in sorted(transforms):
                    puzzle_num = int(transform.split('_')[1].split('.')[0])
                    puzzle_id = f"{dir_name}_{level_dir}_puzzle_{puzzle_num}"

                    puzzles[dir_name][level_num].append({
                        'id': puzzle_id,
                        'number': puzzle_num,
                        'level': level_num,
                        'metadata': PUZZLE_METADATA[level_num],
                        'prompt_file': os.path.join(level_path, f'prompt_{puzzle_num}.txt'),
                        'source_dir': dir_name
                    })

    return puzzles

@app.route('/')
def home():
    puzzles = get_available_puzzles()
    return render_template('index.html', puzzles=puzzles)


@app.route('/puzzle/<puzzle_id>')
def get_puzzle(puzzle_id):
    print(f"DEBUG - Looking for puzzle: {puzzle_id}")
    puzzles = get_available_puzzles()

    # Parse puzzle_id to find it in the nested structure
    source_dir = puzzle_id.split('_')[0]  # 'benchmark' or 'examples'
    level_num = int(puzzle_id.split('_')[2])  # get number after 'level_'
    puzzle_num = int(puzzle_id.split('_')[-1])  # get last number

    # Look for the puzzle in the correct source/level
    if source_dir not in puzzles or level_num not in puzzles[source_dir]:
        print(f"DEBUG - Source {source_dir} or level {level_num} not found")
        return jsonify({'error': 'Puzzle not found'}), 404

    # Find the specific puzzle in the level
    level_puzzles = puzzles[source_dir][level_num]
    puzzle = next((p for p in level_puzzles if p['id'] == puzzle_id), None)

    if not puzzle:
        print(f"DEBUG - Puzzle {puzzle_num} not found in {source_dir} level {level_num}")
        return jsonify({'error': 'Puzzle not found'}), 404

    # Read puzzle prompt
    with open(puzzle['prompt_file'], 'r') as f:
        prompt = f.read()

    return render_template('puzzle.html',
                           puzzle_id=puzzle_id,
                           puzzle=puzzle,
                           prompt=prompt)

@app.route('/api/submit/<puzzle_id>', methods=['POST'])
def submit_solution(puzzle_id):
    puzzles = get_available_puzzles()
    if puzzle_id not in puzzles:
        return jsonify({'error': 'Puzzle not found'}), 404

    data = request.get_json()
    if 'code' not in data:
        return jsonify({'error': 'No code submitted'}), 400

    print(f"Received submission for {puzzle_id}")
    result = docker_sandbox.run_submission(puzzle_id, data['code'])
    print(f"Sandbox result: {result}")

    # Only store in database if submission was successful
    if result.get('success', False):
        with sqlite3.connect('puzzle_bench.db') as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO submissions 
                        (puzzle_id, user_name, total_score, visible_score, hidden_score,
                         execution_time, code_length, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (puzzle_id, 'anonymous', result['total_score'],
                      result['visible_score'], result['hidden_score'],
                      result['execution_time'], len(data['code']),
                      datetime.utcnow()))
            conn.commit()

    return jsonify(result)

@app.route('/api/leaderboard/<puzzle_id>')
def get_leaderboard(puzzle_id):
    with sqlite3.connect('puzzle_bench.db') as conn:
        c = conn.cursor()
        c.execute('''SELECT user_name, total_score, visible_score, hidden_score, 
                    execution_time, code_length, timestamp
                    FROM submissions 
                    WHERE puzzle_id = ?
                    ORDER BY total_score DESC, execution_time ASC
                    LIMIT 10''', (puzzle_id,))
        rows = c.fetchall()

    leaderboard = [{
        'user': row[0],
        'total_score': row[1],
        'visible_score': row[2],
        'hidden_score': row[3],
        'time': row[4],
        'code_length': row[5],
        'timestamp': row[6]
    } for row in rows]

    return jsonify(leaderboard)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

```


### `buffers\generate_buffers.py`

```python

# buffers/generate_buffers.py

import random


def generate_visible_buffers():
    """
    Generate 20 visible test buffers of 64 bytes each, carefully structured
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

    # 18) ASCII text repeated
    text = "Hello, World! "
    buffers.append((text * 5)[:64].encode('ascii'))

    # 19) Fibonacci sequence mod 256
    fib = bytearray(64)
    fib[0], fib[1] = 1, 1
    for i in range(2, 64):
        fib[i] = (fib[i-1] + fib[i-2]) % 256
    buffers.append(bytes(fib))

    # 20) Random but reproducible
    random.seed(4)  # Fixed seed for reproducibility
    buffers.append(bytes([random.randint(0, 255) for _ in range(64)]))

    return buffers


def generate_hidden_buffers():
    """
    Generate 20 hidden validation buffers, progressively more complex.
    """
    random.seed(1337)  # Different seed for hidden buffers
    buffers = []

    # 1-4) More complex patterns
    buffers.append(bytes([x ^ (x >> 4) for x in range(64)]))  # XOR pattern
    buffers.append(bytes([(x * 7 + 13) % 256 for x in range(64)]))  # Linear transform
    buffers.append(bytes([pow(x, 2, 256) for x in range(64)]))  # Square numbers
    buffers.append(bytes([pow(3, x, 256) for x in range(64)]))  # Powers of 3

    # 5-8) Mixed patterns
    for _ in range(4):
        buf = bytearray(64)
        pattern_length = random.randint(2, 8)
        pattern = [random.randint(0, 255) for _ in range(pattern_length)]
        for i in range(64):
            buf[i] = pattern[i % pattern_length]
        buffers.append(bytes(buf))

    # 9-12) Structured random
    for _ in range(4):
        buf = bytearray(64)
        for i in range(64):
            buf[i] = (i * random.randint(1, 7) + random.randint(0, 255)) % 256
        buffers.append(bytes(buf))

    # 13-16) More text patterns with different encodings
    texts = ["Test 123!", "Python<>", "0xCAFE :)", "Binary..."]
    for text in texts:
        buf = bytearray(64)
        encoded = text.encode('utf-8')
        buf[:len(encoded)] = encoded
        for i in range(len(encoded), 64):
            buf[i] = random.randint(0, 255)
        buffers.append(bytes(buf))

    # 17-20) Pure random buffers
    for _ in range(4):
        buffers.append(bytes([random.randint(0, 255) for _ in range(64)]))

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

    prompt = """Below is a puzzle involving 20 input buffers and their transformed outputs.
Each buffer is exactly 64 bytes, shown in hex.

Your task: Figure out the logic of the transformation used to go from the INPUT to the OUTPUT.
Then, provide a Python function that, given any new 64-byte buffer, will produce the correct transformed output.

def transform(data: bytes) -> bytes:
   # Transform logic
   return bytes

Here are the 20 input (SRC) buffers in hex (one line per buffer):
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
    hidden_buffers = generate_hidden_buffers()

    # Save the prompt header for later use
    with open('shared/prompt_header.txt', 'w') as f:
        f.write(prompt_header)

    # Save the buffers
    save_buffers(visible_buffers, 'visible')
    save_buffers(hidden_buffers, 'hidden')

    print("Generated prompt header and saved to 'buffers/shared/prompt_header.txt'")

```


### `gta_benchmark.md`

```

# **Project: GTA-Benchmark (Guess the Transform Algorithm Benchmark)**

## **Overview**
GTA-Benchmark (Guess the Transform Algorithm Benchmark) is a web-based benchmarking tool designed to test the algorithmic reasoning capabilities of AI models and humans. Each puzzle challenges participants to reverse-engineer a hidden byte transformation algorithm by examining input-output pairs. The system provides a set of 20 visible test cases for analysis and 20 hidden test cases for validation, with all buffers being exactly 64 bytes.

Participants are provided with a set of shared input buffers and the corresponding transformed outputs. Their goal is to guess the transformation logic by submitting Python code that replicates the hidden algorithm. Scores are awarded based on accuracy, execution time, and solution size, with features like leaderboards, multiple difficulty levels, and automated scoring.

---

## **Purpose**

As AI systems become increasingly capable, traditional benchmarks like solving human-designed tests or datasets are getting saturated. The purpose of GTA-Benchmark is to introduce a new category of evaluation that:
1. Tests **algorithmic reasoning** and the ability to deduce patterns.
2. Simulates **real-world black-box problems**, where input-output relationships need to be reverse-engineered.
3. Provides a scalable and adaptive way to assess AI capabilities across varying levels of complexity.

This benchmark is not only for AI systems but also for human enthusiasts and developers who want to challenge their reasoning and problem-solving skills.

---

## Key Features

1. **Standardized Testing Format**
   - 20 visible test cases for analysis
   - 20 hidden test cases for validation
   - All buffers exactly 64 bytes
   - Instant feedback on both visible and hidden tests

2. **Web Interface**
   - Easy puzzle selection by difficulty level
   - One-click puzzle prompt copying
   - Real-time feedback on submissions
   - Live leaderboard tracking

3. **Secure Execution**
   - Docker-based sandboxing
   - Resource limits enforcement
   - Safe code execution environment

4. **Performance Metrics**
   - Separate scoring for visible and hidden tests
   - Execution time tracking
   - Code size measurement
   - Comprehensive leaderboard
   
---

## **Goals**

### **Primary Goals**
1. **Develop a dynamic and scalable AI benchmark**:
   - Create puzzles with varying complexity levels and transformation logic.
   - Support automated scoring, feedback, and result tracking.

2. **Enhance AI's understanding of algorithmic reasoning**:
   - Move beyond static datasets by testing AI's ability to deduce transformations dynamically.

3. **Enable reproducibility and fairness**:
   - Provide a fixed set of shared input buffers and transformation outputs for consistent scoring.

4. **Promote competition and collaboration**:
   - Introduce leaderboards for tracking the best solutions.
   - Allow researchers, developers, and AI enthusiasts to compare performance.

---

## **Use Cases**

1. **AI Benchmarking**:
   - Test and compare state-of-the-art AI models for algorithmic reasoning.
   - Evaluate the ability to infer logic and patterns.

2. **Learning and Development**:
   - Provide developers with a hands-on tool to practice reverse-engineering and reasoning skills.
   - Act as an educational platform for teaching algorithms and pattern recognition.

3. **Research in AI Reasoning**:
   - A testing ground for understanding how AI models approach complex reasoning tasks.
   - Provide insights into strengths and limitations of different AI architectures.

4. **Competitions and Challenges**:
   - Host public challenges to engage developers and AI researchers.
   - Foster a competitive environment with leaderboards and prizes.

---

## Project Structure
```python
GTA-Benchmark/
+-- app.py                   # Flask web server
+-- sandbox.py              # Docker sandbox implementation
+-- main.py                # Main entry point
+-- requirements.txt      # Project dependencies
|
+-- buffers/
¦   +-- generate_buffers.py # Buffer generation script
¦   +-- shared/             # Standardized test buffers
¦       +-- visible_*.bin   # 20 visible test buffers
¦       +-- hidden_*.bin    # 20 hidden test buffers
¦       +-- prompt_header.txt  # Standard puzzle prompt header
|
+-- puzzles/
¦   +-- examples/          # Example puzzles for local testing
¦   ¦   +-- level_1/      # Basic examples
¦   ¦   ¦   +-- transform_*.py
¦   ¦   ¦   +-- visible_outputs_*.bin
¦   ¦   ¦   +-- hidden_outputs_*.bin
¦   ¦   ¦   +-- prompt_*.txt
¦   ¦   +-- level_2/      # Advanced examples
¦   +-- benchmark/        # Real benchmark puzzles (gitignored)
¦       +-- level_1/      # Basic single-byte operations
¦       ¦   +-- transform_*.py
¦       ¦   +-- visible_outputs_*.bin
¦       ¦   +-- hidden_outputs_*.bin
¦       ¦   +-- prompt_*.txt
¦       +-- level_2/      # Advanced operations
¦       +-- [future levels]
|
+-- scripts/
¦   +-- apply_transforms.py  # Generates outputs and prompts
|
+-- templates/
¦   +-- index.html        # Level selection page
¦   +-- puzzle.html       # Puzzle submission interface
|
+-- docs/                # Documentation
```

---

## Puzzle Levels and Progression

The benchmark provides a carefully designed progression of puzzle difficulties:

### Level 1: Single Byte - Basic
- Window Size: 1 byte
- Operations: 1-3 operations per byte
- No state tracking
- Examples: XOR, addition, simple arithmetic combinations

### Level 2: Single Byte - Advanced
- Window Size: 1 byte
- Operations: 3-6 operations per byte
- No state tracking
- Features: Conditionals, bit manipulation, multiple operations

[Future levels will introduce more complex concepts like:]
- Byte pair operations
- Multi-byte blocks
- State tracking
- Position-dependent transforms
- Multi-pass algorithms

## Test Buffer Design

Each puzzle includes carefully crafted test buffers to help understand the transformation:

### Visible Test Buffers (20 total)
1. Basic patterns (zeros, ones)
2. Single byte variations
3. Sequential patterns
4. Alternating patterns
5. Common bit patterns
6. Powers of 2 sequences
7. ASCII text
8. Controlled random data

### Hidden Test Buffers (20 total)
- More complex patterns
- Different sequences
- Various encodings
- Pure random data
- Edge cases

This design ensures that visible buffers help in pattern recognition while hidden buffers validate the complete solution.

## Scoring System

Submissions are evaluated on multiple criteria:
1. **Accuracy**
   - Visible test cases (50% of total score)
   - Hidden test cases (50% of total score)
   - Each test case must produce exact byte matches

2. **Performance Metrics**
   - Execution time in seconds
   - Solution code length in characters
   - Resource usage within Docker container limits

The leaderboard tracks:
- Total score (percentage)
- Separate visible/hidden scores
- Execution time
- Code size

---

## Using the Benchmark

### For Participants
1. Select a puzzle level matching your skill
2. Copy the puzzle prompt showing input/output pairs
3. Analyze the visible test cases to understand the transform
4. Write a Python function matching the required signature:
   ```python
   def transform(data: bytes) -> bytes:
       # Your solution here
       return transformed_data
5. Submit your solution for instant feedback
6. Check your score on both visible and hidden tests
7. Compare your performance on the leaderboard

### For Researchers

1. Standardized evaluation of algorithmic reasoning
2. Comparable results across different AI models
3. Clear metrics for measuring performance
4. Scalable difficulty levels for benchmarking
       
---

## **Development Status**

### **Phase 1: Completed**
- Generated standardized test buffers (20 visible + 20 hidden)
- Implemented first two difficulty levels
- Built Flask server with puzzle selection and submission
- Integrated Docker sandbox for secure execution
- Implemented leaderboard system

### **Current Phase: Implementation**
1. Completing Single-Byte Operations
   - Implementing remaining Level 1 puzzles (1-5)
   - Implementing remaining Level 2 puzzles (1-5)
   - Testing and verifying all transforms

2. Docker Sandbox Refinement
   - Testing resource limits and security
   - Improving error handling and feedback
   - Optimizing execution pipeline

3. Web Interface Polish
   - Refining puzzle submission interface
   - Enhancing leaderboard display
   - Improving puzzle selection page
   
### **Next Phase: Expansion**
1. Deploy on DigitalOcean
2. Add more complex transformations
3. Implement user authentication
4. Add competition features

---

## **Technical Details**

### **Docker Configuration**
- Base Image: python:3.9-slim
- Memory Limit: 256MB
- Execution Timeout: 30 seconds
- Network Access: Disabled
- Volume Mounts: Read-only puzzle and test data

### **File Organization**
- Input Buffers: 64-byte binary files (visible_XX.bin, hidden_XX.bin)
- Output Buffers: 64-byte binary files per puzzle
- Transforms: Python files with standard signature
- Database: SQLite with submissions table tracking scores, times, and metadata

### **Submission Processing**
- Code validation and security checks
- Execution in isolated container
- Testing against 40 test cases (20 visible + 20 hidden)
- Performance metrics collection
- Real-time result calculation and storage

---

## **Sample Problem Prompt**
"""Below is a puzzle involving 20 input buffers and their transformed outputs.
Each buffer is exactly 64 bytes, shown in hex.

Your task: Figure out the logic of the transformation used to go from the INPUT to the OUTPUT.
Then, provide a Python function that, given any new 64-byte buffer, will produce the correct transformed output.

def transform(data: bytes) -> bytes:
   # Transform logic
   return bytes

Here are the 20 input (SRC) buffers in hex (one line per buffer):
INPUT #01: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
INPUT #02: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
INPUT #03: 01000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
INPUT #04: 02000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
INPUT #05: 80000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
INPUT #06: aa000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
INPUT #07: 00ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
INPUT #08: f0ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
INPUT #09: 0fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
INPUT #10: 55ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
INPUT #11: 000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f
INPUT #12: fffefdfcfbfaf9f8f7f6f5f4f3f2f1f0efeeedecebeae9e8e7e6e5e4e3e2e1e0dfdedddcdbdad9d8d7d6d5d4d3d2d1d0cfcecdcccbcac9c8c7c6c5c4c3c2c1c0
INPUT #13: aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55
INPUT #14: 55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa55aa
INPUT #15: f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0
INPUT #16: 0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f
INPUT #17: 01010101010101010202020202020202040404040404040408080808080808081010101010101010202020202020202040404040404040408080808080808080
INPUT #18: 48656c6c6f2c20576f726c64212048656c6c6f2c20576f726c64212048656c6c6f2c20576f726c64212048656c6c6f2c20576f726c64212048656c6c6f2c2057
INPUT #19: 0101020305080d1522375990e97962db3d18556dc22ff12011314273b528dd05e2e7c9b07929a2cb6d38a5dd825fe140216182e36548adf5a29739d009d9e2bb
INPUT #20: 789b34caf54f2e220acd941e71b88d5836866d0d858b63549e94be2cacc67f5b7ef28f2d9903959f63d3d893dce752779c84162917ec8ff1af4a6422d367e18d

And here are the corresponding transformed outputs (DST) in hex:
OUTPUT #01: 07070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707
OUTPUT #02: f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7
OUTPUT #03: 07070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707
OUTPUT #04: 07070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707
OUTPUT #05: 87070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707
OUTPUT #06: a7070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707
OUTPUT #07: 07f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7
OUTPUT #08: f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7
OUTPUT #09: 07f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7
OUTPUT #10: 57f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7
OUTPUT #11: 07070707070707070707070707070707171717171717171717171717171717172727272727272727272727272727272737373737373737373737373737373737
OUTPUT #12: f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7e7e7e7e7e7e7e7e7e7e7e7e7e7e7e7e7d7d7d7d7d7d7d7d7d7d7d7d7d7d7d7d7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7
OUTPUT #13: a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757
OUTPUT #14: 57a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a757a7
OUTPUT #15: f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7
OUTPUT #16: 07070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707070707
OUTPUT #17: 07070707070707070707070707070707070707070707070707070707070707071717171717171717272727272727272747474747474747478787878787878787
OUTPUT #18: 47676767672727576777676727274767676767272757677767672727476767676727275767776767272747676767672727576777676727274767676767272757
OUTPUT #19: 070707070707071727375797e77767d737175767c727f72717374777b727d707e7e7c7b77727a7c76737a7d78757e747276787e76747a7f7a79737d707d7e7b7
OUTPUT #20: 779737c7f747272707c7971777b7875737876707878767579797b727a7c7775777f787279707979767d7d797d7e757779787172717e787f7a7476727d767e787

Good luck! Remember, the transformation is the same for all 20 buffers."""

---

## **Future Enhancements**

1. **User Management**
   - User registration and profiles
   - Solution history tracking
   - Achievement system

2. **Enhanced Competition Features**
   - Time-limited challenges
   - Weekly/monthly competitions
   - Team competitions

3. **Platform Expansion**
   - API access for automated testing
   - Support for additional programming languages
   - Integration with CI/CD pipelines for AI testing

4. **Educational Features**
   - Tutorial system for beginners
   - Hint system for difficult puzzles
   - Community solutions sharing
   
---

## **Conclusion**

GTA-Benchmark is an innovative benchmarking platform that pushes the boundaries of AI reasoning and reverse-engineering capabilities. By providing a structured yet flexible framework, it aims to become a valuable tool for AI researchers, developers, and enthusiasts. Through dynamic puzzles, secure evaluation, and public leaderboards, the benchmark will foster competition, collaboration, and advancements in AI and human problem-solving.

**Get ready to reverse-engineer, innovate, and compete!**

```


### `main.py`

```python

# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


```


### `puzzle_bench.db`

```

<binary or non-text file: not displayed>

```


### `puzzles\benchmark\level_1\transform_1.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # 1.1 - Single XOR (simplest bitwise op)
    return bytes([b ^ 0x55 for b in data])

```


### `puzzles\benchmark\level_1\transform_2.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # 1.2 - Single addition (simplest arithmetic)
    return bytes([(b + 0x10) % 256 for b in data])

```


### `puzzles\benchmark\level_1\transform_3.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # 1.3 - Simple AND then addition (introduces AND)
    return bytes([((b & 0xF0) + 0x07) % 256 for b in data])

```


### `puzzles\benchmark\level_1\transform_4.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # 1.4 - Multiply then add
    return bytes([(b * 3 + 7) % 256 for b in data])

```


### `puzzles\benchmark\level_1\transform_5.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # 1.5 - XOR then add
    return bytes([(b ^ 0x55 + 31) % 256 for b in data])

```


### `puzzles\benchmark\level_2\transform_1.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # 2.1 fixed precedence
    return bytes([((((b << 3) & 0xFF) | (b >> 5)) + 0xA0) % 256 for b in data])

```


### `puzzles\benchmark\level_2\transform_2.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # 2.2 - Swap nibbles (pure bit manipulation)
    return bytes([(b & 0xF0) >> 4 | (b & 0x0F) << 4 for b in data])

```


### `puzzles\benchmark\level_2\transform_3.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # 2.3 - Conditional transform (introduces branching)
    return bytes([b ^ 0xAA if b & 0x80 else b ^ 0x55 for b in data])

```


### `puzzles\benchmark\level_2\transform_4.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # 2.4 - Multiple ops combining previous concepts
    return bytes([(((b << 2) & 0xFF) + 0x33) % 256 ^ (b >> 4) for b in data])


```


### `puzzles\benchmark\level_2\transform_5.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # 2.5 - Most complex single-byte (all concepts)
    return bytes([
        (((b << 1) & 0xFF) + ((b >> 1) ^ 0xAA)) % 256 if b > 0x7F
        else ((b + 0x35) ^ (b >> 2)) % 256
        for b in data
    ])

```


### `puzzles\benchmark\readme.md`

```

# Benchmark Puzzles

This directory contains the actual benchmark puzzle sets used to evaluate AI models and participants.

The puzzle files are not included in the public repository to maintain the integrity of the benchmark. 

When deploying, these files are pulled from a private repository.

To test the system locally, please refer to the puzzles in the `examples` directory.

```


### `puzzles\examples\level_1\transform_1.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # Single XOR (simplest bitwise op)
    return bytes([b ^ 0xA5 for b in data])

```


### `puzzles\examples\level_1\transform_2.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # Simple AND then addition (introduces AND)
    return bytes([((b & 0xF5) + 0x0B) % 256 for b in data])

```


### `puzzles\examples\level_1\transform_3.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # XOR then add
    return bytes([(b ^ 0xAF + 15) % 256 for b in data])

```


### `puzzles\examples\level_1\transform_4.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # Conditional transform (introduces branching)
    return bytes([b ^ 0x55 if b & 0x40 else b ^ 0xAA for b in data])

```


### `puzzles\examples\level_1\transform_5.py`

```python

def hidden_transform(data: bytes) -> bytes:
    # Multiple ops combining previous concepts
    return bytes([(((b << 3) & 0xEF) + 0x13) % 256 ^ (b >> 4) for b in data])


```


### `sandbox.py`

```python

# sandbox.py

import docker
import tempfile
import os
from pathlib import Path
import json


class DockerSandbox:
    def __init__(self):
        self.client = docker.from_env()
        self.image_name = "python:3.9-slim"
        # Store project root at initialization
        self.project_root = os.path.abspath(os.getcwd())

        print("Initializing Docker sandbox...")
        try:
            self.client.images.pull(self.image_name)
            print(f"Successfully pulled {self.image_name}")
        except Exception as e:
            print(f"Error pulling Docker image: {e}")
            raise

    def run_submission(self, puzzle_id: str, user_code: str) -> dict:
        print(f"Running submission for puzzle {puzzle_id}")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Save user code
            with open(tmp_path / "solution.py", "w") as f:
                f.write(user_code)
            print("Saved user solution")

            # Create runner script
            runner_script = """
import sys
import json
import time
import os
from pathlib import Path

def load_buffers(prefix):
    buffers = []
    for i in range(1, 21):  # Load all 20 buffers
        with open(f"/buffers/shared/{prefix}_{i:02d}.bin", "rb") as f:
            buffers.append(f.read())
    return buffers

def load_expected_outputs(puzzle_dir, puzzle_num):
    visible_outputs = []
    hidden_outputs = []
    
    # Load visible outputs
    with open(f"{puzzle_dir}/visible_outputs_{puzzle_num}.bin", "rb") as f:
        for _ in range(20):  # 20 buffers
            visible_outputs.append(f.read(64))
            
    # Load hidden outputs
    with open(f"{puzzle_dir}/hidden_outputs_{puzzle_num}.bin", "rb") as f:
        for _ in range(20):  # 20 buffers
            hidden_outputs.append(f.read(64))
            
    return visible_outputs, hidden_outputs

def run_tests():
    try:
        start_time = time.time()
        
        print("Current directory contents:", flush=True)
        os.system("ls -la /puzzle")  # Let's see what files we actually have
        
        # Import the user's transform function
        from solution import transform
        print("Successfully imported user solution", flush=True)
        
        # Load inputs
        try:
            print("Loading input buffers...", flush=True)
            visible_inputs = load_buffers('visible')
            hidden_inputs = load_buffers('hidden')
            print(f"Loaded {len(visible_inputs)} visible and {len(hidden_inputs)} hidden inputs", flush=True)
        except Exception as e:
            print(f"Error loading inputs: {e}", flush=True)
            raise
            
        # Load expected outputs
        try:
            print("Loading expected outputs...", flush=True)
            print("Files in /puzzle:", os.listdir("/puzzle"), flush=True)
            puzzle_num = os.environ["PUZZLE_NUM"]  # Get puzzle number from environment
            
            with open(os.path.join("/puzzle", f"visible_outputs_{puzzle_num}.bin"), "rb") as f:
                visible_outputs = []
                for _ in range(20):
                    visible_outputs.append(f.read(64))
            print("Loaded visible outputs", flush=True)
                    
            with open(os.path.join("/puzzle", f"hidden_outputs_{puzzle_num}.bin"), "rb") as f:
                hidden_outputs = []
                for _ in range(20):
                    hidden_outputs.append(f.read(64))
            print("Loaded hidden outputs", flush=True)
        except Exception as e:
            print(f"Error loading outputs: {e}", flush=True)
            raise
                                
        # Run transform on all inputs
        visible_results = []
        hidden_results = []

        for buf in visible_inputs:
            try:
                result = transform(buf)
                if not isinstance(result, bytes) or len(result) != 64:
                    raise ValueError("Transform must return 64 bytes")
                visible_results.append(result)
            except Exception as e:
                print(f"Error running transform: {e}", flush=True)
                raise

        for buf in hidden_inputs:
            try:
                result = transform(buf)
                if not isinstance(result, bytes) or len(result) != 64:
                    raise ValueError("Transform must return 64 bytes")
                hidden_results.append(result)
            except Exception as e:
                print(f"Error running transform: {e}", flush=True)
                raise

        # Calculate scores
        visible_correct = sum(1 for a, b in zip(visible_results, visible_outputs) if a == b)
        hidden_correct = sum(1 for a, b in zip(hidden_results, hidden_outputs) if a == b)

        end_time = time.time()
        execution_time = end_time - start_time

        result = {
            "success": True,
            "visible_score": visible_correct / 20,
            "hidden_score": hidden_correct / 20,
            "total_score": (visible_correct + hidden_correct) / 40,
            "execution_time": execution_time,
            "visible_correct": visible_correct,
            "hidden_correct": hidden_correct
        }

        print(json.dumps(result), flush=True)
        return result

    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(result), flush=True)
        return result

if __name__ == "__main__":
    run_tests()
"""
            with open(tmp_path / "runner.py", "w") as f:
                f.write(runner_script)
            print("Created test runner")

            try:
                # Parse puzzle ID components
                puzzle_parts = puzzle_id.split('_')
                source_dir = puzzle_parts[0]  # 'benchmark' or 'examples'
                level_dir = f"{puzzle_parts[1]}/{puzzle_parts[2]}"  # already includes 'level_'
                puzzle_num = puzzle_parts[-1]  # Get last part as puzzle number

                buffers_path = os.path.join(self.project_root, "buffers", "shared")
                puzzle_dir = os.path.join(self.project_root, "puzzles", source_dir, level_dir)

                if not os.path.exists(buffers_path):
                    return {"error": "Buffer path not found"}
                if not os.path.exists(puzzle_dir):
                    return {"error": f"Puzzle directory not found: {puzzle_dir}"}

                print(f"DEBUG - Mounting buffers from: {buffers_path}")
                print(f"DEBUG - Mounting puzzle dir from: {puzzle_dir}")
                print(f"DEBUG - Looking for outputs with number: {puzzle_num}")

                # Run the container
                print("Starting container...")
                result = self.client.containers.run(
                    self.image_name,
                    ["python", "-u", "/workspace/runner.py"],
                    environment={
                        "PUZZLE_NUM": puzzle_num  # Pass puzzle number to container
                    },
                    volumes={
                        str(tmp_path): {"bind": "/workspace", "mode": "ro"},
                        buffers_path: {"bind": "/buffers/shared", "mode": "ro"},
                        puzzle_dir: {"bind": "/puzzle", "mode": "ro"}
                    },
                    mem_limit="256m",
                    network_disabled=True,
                    remove=True
                )

                # Process the output
                output = result.decode('utf-8').strip()
                print("\nDEBUG - Container Output lines:")
                print("-" * 50)
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    print(f"Line {i}: {repr(line)}")
                print("-" * 50)

                # Look for the last JSON line as our result
                for line in reversed(lines):
                    line = line.strip()
                    try:
                        result_dict = json.loads(line)
                        print("DEBUG - Successfully parsed JSON:", result_dict)
                        return result_dict
                    except json.JSONDecodeError:
                        continue

                return {"error": "No valid result found"}

            except Exception as e:
                print(f"Container error: {e}")
                return {"error": str(e)}

```


### `scripts\apply_transforms.py`

```python

# scripts/apply_transforms.py

import os
import importlib.util
from pathlib import Path


def load_transform(module_path):
    """
    Dynamically load the hidden_transform function from a given module path.
    """
    spec = importlib.util.spec_from_file_location("transform_module", module_path)
    transform_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(transform_module)
    return transform_module.hidden_transform


def load_all_buffers(shared_directory='../buffers/shared'):
    """
    Load both visible and hidden input buffers.
    Returns (visible_buffers, hidden_buffers)
    """
    visible_buffers = []
    hidden_buffers = []

    # Load visible buffers
    seen_bytes = set()
    for i in range(1, 21):
        filepath = os.path.join(shared_directory, f'visible_{i:02d}.bin')
        with open(filepath, 'rb') as f:
            buf = f.read()
            visible_buffers.append(buf)
            seen_bytes.update(buf)

    missing_bytes = set(range(256)) - seen_bytes

    print(f"Total unique bytes in visible inputs: {len(seen_bytes)}")
    print(f"Number of missing bytes in visible inputs: {len(missing_bytes)}")
    print("Missing byte values on input buffers: ")
    print([f"0x{x:02X}" for x in sorted(list(missing_bytes))])

    # Load hidden buffers
    for i in range(1, 21):
        filepath = os.path.join(shared_directory, f'hidden_{i:02d}.bin')
        with open(filepath, 'rb') as f:
            hidden_buffers.append(f.read())

    return visible_buffers, hidden_buffers


def load_prompt_header(shared_directory='../buffers/shared'):
    """
    Load the standardized prompt header.
    """
    with open(os.path.join(shared_directory, 'prompt_header.txt'), 'r') as f:
        return f.read()


def generate_complete_prompt(visible_outputs):
    """
    Generate complete puzzle prompt with outputs.
    """
    prompt_header = load_prompt_header()
    prompt = prompt_header + "\nAnd here are the corresponding transformed outputs (DST) in hex:\n"

    for i, output in enumerate(visible_outputs, 1):
        hex_str = output.hex()
        prompt += f"OUTPUT #{i:02d}: {hex_str}\n"

    prompt += "\nGood luck! Remember, the transformation is the same for all 20 buffers."
    return prompt


def apply_and_save_transforms(root_dir='../puzzles'):
    """
    Recursively discover all transform modules, apply them to all buffers,
    save outputs and generate prompts.
    """
    visible_buffers, hidden_buffers = load_all_buffers()

    # Walk through all subdirectories
    for root, dirs, files in os.walk(root_dir):
        # Look for transform_*.py files
        for file in files:
            if file.startswith('transform_') and file.endswith('.py'):
                transform_file = os.path.join(root, file)

                # Generate output filenames based on transform file number
                output_num = file.split('_')[1].split('.')[0]  # Extract number from transform_N.py

                # Get the directory containing this transform
                transform_dir = os.path.dirname(transform_file)

                # Generate output paths in the same directory
                visible_output_file = os.path.join(transform_dir, f'visible_outputs_{output_num}.bin')
                hidden_output_file = os.path.join(transform_dir, f'hidden_outputs_{output_num}.bin')
                prompt_file = os.path.join(transform_dir, f'prompt_{output_num}.txt')

                try:
                    # Load the hidden_transform function
                    transform = load_transform(transform_file)

                    # Apply transform to all buffers
                    visible_outputs = [transform(buf) for buf in visible_buffers]
                    hidden_outputs = [transform(buf) for buf in hidden_buffers]

                    # Save visible outputs
                    with open(visible_output_file, 'wb') as f_out:
                        for output in visible_outputs:
                            f_out.write(output)

                    # Save hidden outputs
                    with open(hidden_output_file, 'wb') as f_out:
                        for output in hidden_outputs:
                            f_out.write(output)

                    # Generate and save complete prompt
                    prompt = generate_complete_prompt(visible_outputs)
                    with open(prompt_file, 'w') as f_out:
                        f_out.write(prompt)

                    print(f"Applied transform for {transform_file}:")
                    print(f" - Saved visible outputs to {visible_output_file}")
                    print(f" - Saved hidden outputs to {hidden_output_file}")
                    print(f" - Generated prompt at {prompt_file}")

                except Exception as e:
                    print(f"Error applying transform for {transform_file}: {e}")

if __name__ == "__main__":
    apply_and_save_transforms()

```


### `templates\index.html`

```html

<!-- templates/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>GTA Benchmark</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Roboto+Mono&display=swap" rel="stylesheet">
    <style>
        body {
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            font-family: 'Inter', sans-serif;
            background: #f5f5f7;
            color: #1d1d1f;
        }
        h1 {
            text-align: center;
            color: #1d1d1f;
            margin-bottom: 40px;
            font-size: 2.5em;
        }
        .level-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .level-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 40px;
            margin-bottom: 20px;
        }
        .level-info {
            flex: 2;
        }
        .level-info h2 {
            margin: 0 0 10px 0;
            color: #2b2b2b;
        }
        .level-description {
            color: #4b4b4b;
            font-size: 1.1em;
            margin: 0;
        }
        .characteristics-card {
            flex: 1;
            background: #f8f8fa;
            padding: 15px;
            border-radius: 8px;
        }
        .characteristics-title {
            color: #666;
            font-size: 0.9em;
            font-weight: 600;
            margin: 0 0 10px 0;
        }
        .characteristics-list {
            list-style: none;
            padding: 0;
            margin: 0;
            font-size: 0.9em;
            color: #666;
        }
        .characteristics-list li {
            margin-bottom: 5px;
        }
        .characteristics-list li strong {
            color: #4b4b4b;
        }
        .puzzle-links {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        .puzzle-link {
            display: inline-block;
            padding: 8px 16px;
            background: #007aff;
            color: white;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9em;
            transition: background 0.2s;
        }
        .puzzle-link:hover {
            background: #0055b3;
        }
        @media (max-width: 768px) {
            .level-header {
                flex-direction: column;
                gap: 20px;
            }
            .characteristics-card {
                width: 100%;
            }
        }
    </style>
</head>
<body>
<h1>GTA (Guess The Algorythm) Model Benchmark</h1>

    {% if puzzles.benchmark %}
        {# Show benchmark puzzles if available #}
        {% for level, level_puzzles in puzzles.benchmark|dictsort %}
        <div class="level-card">
            <div class="level-header">
                <div class="level-info">
                    <h2>Level {{level}}: {{level_puzzles[0].metadata.name}}</h2>
                    <p class="level-description">{{level_puzzles[0].metadata.description}}</p>
                </div>

                <div class="characteristics-card">
                    <h3 class="characteristics-title">Level Characteristics</h3>
                    <ul class="characteristics-list">
                        {% for key, value in level_puzzles[0].metadata.complexity.items() %}
                        <li><strong>{{key|title}}:</strong> {{value}}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>

            <div class="puzzle-links">
                {% for puzzle in level_puzzles %}
                <a href="/puzzle/{{puzzle.id}}" class="puzzle-link">Puzzle {{puzzle.number}}</a>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    {% elif puzzles.examples %}
        {# Fall back to examples if no benchmark puzzles #}
        {% for level, level_puzzles in puzzles.examples|dictsort %}
        <div class="level-card">
            <div class="level-header">
                <div class="level-info">
                    <h2>Level {{level}}: {{level_puzzles[0].metadata.name}}</h2>
                    <p class="level-description">{{level_puzzles[0].metadata.description}}</p>
                </div>

                <div class="characteristics-card">
                    <h3 class="characteristics-title">Level Characteristics</h3>
                    <ul class="characteristics-list">
                        {% for key, value in level_puzzles[0].metadata.complexity.items() %}
                        <li><strong>{{key|title}}:</strong> {{value}}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>

            <div class="puzzle-links">
                {% for puzzle in level_puzzles %}
                <a href="/puzzle/{{puzzle.id}}" class="puzzle-link">Puzzle {{puzzle.number}}</a>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    {% endif %}
</body>
</html>

```


### `templates\puzzle.html`

```html

<!-- templates/puzzle.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ puzzle.name }} - Puzzle Benchmark</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Roboto+Mono&display=swap" rel="stylesheet">
    <style>
        body {
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            font-family: 'Inter', sans-serif;
            background: #f5f5f7;
            color: #1d1d1f;
        }

        h1, h2, h3 {
            color: #2b2b2b;
        }

        #puzzle-prompt, #code-editor {
            width: 100%;
            font-family: 'Roboto Mono', monospace;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #ddd;
            background: #fff;
            margin: 15px 0;
        }

        #puzzle-prompt {
            height: 400px;
        }

        #code-editor {
            height: 200px;
        }

        .button {
            padding: 8px 16px;
            background: #007aff;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
            font-size: 0.9em;
            transition: background 0.2s;
        }

        .button:hover {
            background: #0055b3;
        }

        #result {
            margin: 20px 0;
            padding: 15px;
            background: #f8f8fa;
            border-radius: 8px;
            font-size: 0.95em;
        }

        #leaderboard {
            margin-top: 30px;
        }

        .leaderboard-entry {
            display: flex;
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .rank {
            font-size: 1.2em;
            font-weight: 600;
            width: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #007aff;
            color: white;
            border-radius: 6px;
            margin-right: 15px;
        }

        .details {
            flex: 1;
        }

        .user-score {
            font-size: 1.1em;
            margin-bottom: 5px;
        }

        .score-breakdown {
            color: #666;
            margin-bottom: 3px;
        }

        .metrics {
            font-size: 0.9em;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="header-info">
        <h1>Level {{puzzle.level}}: {{puzzle.metadata.name}}</h1>
        <h2>Puzzle {{puzzle.puzzle_number}}</h2>
    </div>

    <div>
        <button class="button" onclick="copyPrompt()">Copy Puzzle Prompt</button>
        <textarea id="puzzle-prompt" readonly>{{prompt}}</textarea>
    </div>

    <div>
        <h3>Submit your solution:</h3>
        <textarea id="code-editor">def transform(data: bytes) -> bytes:
    # Your solution here
    return data</textarea>

        <button class="button" onclick="submitSolution()">Submit</button>
    </div>

    <div id="result"></div>

    <div id="leaderboard">
        <h3>Leaderboard</h3>
        <div id="leaderboard-content"></div>
    </div>

    <script>
        function copyPrompt() {
            const promptText = document.getElementById('puzzle-prompt');
            promptText.select();
            document.execCommand('copy');
            window.getSelection().removeAllRanges();
            alert('Puzzle prompt copied to clipboard!');
        }

        async function submitSolution() {
            const code = document.getElementById('code-editor').value;
            try {
                const response = await fetch('/api/submit/{{puzzle_id}}', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code })
                });
                const result = await response.json();
                document.getElementById('result').innerHTML =
                    `Score: ${(result.total_score * 100).toFixed(1)}%<br>` +
                    `Visible Test Cases: ${result.visible_correct}/20<br>` +
                    `Hidden Test Cases: ${result.hidden_correct}/20<br>` +
                    `Time: ${result.execution_time.toFixed(3)}s`;
                loadLeaderboard();
            } catch (error) {
                document.getElementById('result').innerHTML =
                    `Error: ${error.message}`;
            }
        }

        async function loadLeaderboard() {
            try {
                const response = await fetch('/api/leaderboard/{{puzzle_id}}');
                const leaderboard = await response.json();
                const content = leaderboard.map((entry, i) => `
                    <div class="leaderboard-entry">
                        <div class="rank">#${i + 1}</div>
                        <div class="details">
                            <div class="user-score">
                                <strong>${entry.user}</strong> -
                                Total: ${(entry.total_score * 100).toFixed(1)}%
                            </div>
                            <div class="score-breakdown">
                                Visible: ${(entry.visible_score * 100).toFixed(1)}% |
                                Hidden: ${(entry.hidden_score * 100).toFixed(1)}%
                            </div>
                            <div class="metrics">
                                Time: ${entry.time.toFixed(3)}s |
                                Code Length: ${entry.code_length} chars
                            </div>
                        </div>
                    </div>
                `).join('');

                document.getElementById('leaderboard-content').innerHTML = content;
            } catch (error) {
                document.getElementById('leaderboard-content').innerHTML =
                    `Error loading leaderboard: ${error.message}`;
            }
        }

        // Load leaderboard on page load
        loadLeaderboard();
    </script>
</body>
</html>

```

