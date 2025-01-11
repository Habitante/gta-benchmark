# app.py
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

from pathlib import Path
from sandbox import DockerSandbox
from flask import Flask, request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import docker
import tempfile
import sqlite3


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# After creating the Flask app
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

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
        'name': 'Intro to Multi-Byte',
        'description': 'Position-based operations and simple dependencies',
        'complexity': {
            'window': '1-2 bytes or position i',
            'operations': '1-3 ops per byte',
            'state': 'position-based, simple branching',
            'features': 'position indexing, even/odd logic, previous byte reference'
        }
    },
    4: {
        'name': 'Basic Multi-Pass',
        'description': 'Two-pass transforms and 2D indexing without state',
        'complexity': {
            'window': '1-2 bytes or 2D indexing',
            'operations': '2-5 ops per byte',
            'state': 'none',
            'features': 'multi-pass, 2D transforms, position-based blocks'
        }
    },
    5: {
        'name': 'State Introduction',
        'description': 'Running state and block-based operations',
        'complexity': {
            'window': '1+ bytes with state',
            'operations': '2-5 ops per byte',
            'state': 'running state, toggles',
            'features': 'state tracking, block operations'
        }
    },
    6: {
        'name': 'Complex Multi-Pass',
        'description': 'Advanced passes with blocks and feedback',
        'complexity': {
            'window': 'multiple bytes, blocks',
            'operations': '3-6 ops per byte',
            'state': 'block-based feedback, toggles',
            'features': 'multi-pass with feedback, block transforms'
        }
    },
    7: {
        'name': 'Advanced Combinations',
        'description': 'Checksums, multi-pass feedback, and block operations',
        'complexity': {
            'window': 'full buffer or blocks',
            'operations': '4-7 ops per byte',
            'state': 'checksums, block feedback',
            'features': 'checksum-based transforms, complex multi-pass, block shuffling'
        }
    },
    8: {
        'name': 'State Machines and Complex Dependencies',
        'description': 'Multi-state transforms with data-dependent behavior',
        'complexity': {
            'window': 'full buffer with local windows',
            'operations': '5-8 ops per byte',
            'state': 'multiple running states, data-driven behavior',
            'features': 'running checksums, multi-condition branching, cross-referencing states'
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
@limiter.limit("20 per minute")  # More strict limit for submissions
def submit_solution(puzzle_id):
    puzzles = get_available_puzzles()

    # Parse puzzle_id to find it in the nested structure
    source_dir = puzzle_id.split('_')[0]  # 'benchmark' or 'examples'
    level_num = int(puzzle_id.split('_')[2])  # get number after 'level_'
    puzzle_num = int(puzzle_id.split('_')[-1])  # get last number

    # Look for the puzzle in the correct source/level
    if source_dir not in puzzles or level_num not in puzzles[source_dir]:
        return jsonify({'error': 'Puzzle not found'}), 404

    # Find the specific puzzle in the level
    level_puzzles = puzzles[source_dir][level_num]
    puzzle = next((p for p in level_puzzles if p['id'] == puzzle_id), None)

    if not puzzle:
        return jsonify({'error': 'Puzzle not found'}), 404

    data = request.get_json()
    if 'code' not in data:
        return jsonify({'error': 'No code submitted'}), 400

    print(f"Received submission for {puzzle_id}")
    result = docker_sandbox.run_submission(puzzle_id, data['code'])
    print(f"Sandbox result: {result}")

    # Get user identifier from IP
    user_id = get_user_identifier(request)

    # Only store in database if submission was successful
    if result.get('success', False):
        with sqlite3.connect('puzzle_bench.db') as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO submissions 
                        (puzzle_id, user_name, total_score, visible_score, hidden_score,
                         execution_time, code_length, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (puzzle_id, user_id, result['total_score'],  # Changed from 'anonymous' to user_id
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

def get_user_identifier(request):
    ip = request.remote_addr
    hash_id = hashlib.md5(ip.encode()).hexdigest()[:8]
    return f"User_{hash_id}"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)