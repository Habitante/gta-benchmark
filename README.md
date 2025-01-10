# GTA Benchmark (Guess The Algorithm)

A tool for testing AI reasoning capabilities through reverse-engineering of byte transformations.

## Overview
GTA-Benchmark challenges participants to reverse-engineer hidden transformation algorithms by examining input-output pairs. Each puzzle provides 20 visible test cases for analysis and 20 hidden test cases for validation.

## Structure
- Example puzzles are included in `puzzles/examples/`
- Actual benchmark puzzles are kept private
- All test buffers are 64 bytes

## Local Development
1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Run the server: `python app.py`
4. Access the web interface at `http://localhost:5000`