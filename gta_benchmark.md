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