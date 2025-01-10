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