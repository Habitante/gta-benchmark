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
    for i in range(1, 25):  # Load all 24 buffers
        with open(f"/buffers/shared/{prefix}_{i:02d}.bin", "rb") as f:
            buffers.append(f.read())
    return buffers

def load_expected_outputs(puzzle_dir, puzzle_num):
    visible_outputs = []
    hidden_outputs = []
    
    # Load visible outputs
    with open(f"{puzzle_dir}/visible_outputs_{puzzle_num}.bin", "rb") as f:
        for _ in range(24):  # 24 buffers
            visible_outputs.append(f.read(64))
            
    # Load hidden outputs
    with open(f"{puzzle_dir}/hidden_outputs_{puzzle_num}.bin", "rb") as f:
        for _ in range(24):  # 24 buffers
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
                for _ in range(24):
                    visible_outputs.append(f.read(64))
            print("Loaded visible outputs", flush=True)
                    
            with open(os.path.join("/puzzle", f"hidden_outputs_{puzzle_num}.bin"), "rb") as f:
                hidden_outputs = []
                for _ in range(24):
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
            "visible_score": visible_correct / 24,
            "hidden_score": hidden_correct / 24,
            "total_score": (visible_correct + hidden_correct) / 48,
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
                level_dir = f"{puzzle_parts[1]}_{puzzle_parts[2]}"  # already includes 'level_'
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

                # Create container with configuration
                container = self.client.containers.create(
                    self.image_name,
                    ["python", "-u", "/workspace/runner.py"],
                    environment={
                        "PUZZLE_NUM": puzzle_num
                    },
                    volumes={
                        str(tmp_path): {"bind": "/workspace", "mode": "ro"},
                        buffers_path: {"bind": "/buffers/shared", "mode": "ro"},
                        puzzle_dir: {"bind": "/puzzle", "mode": "ro"}
                    },
                    mem_limit="64m",
                    network_disabled=True,
                    read_only=True,
                    pids_limit=100
                )

                try:
                    # Start container and wait for result
                    container.start()
                    result = container.wait(timeout=3)

                    # Get container output
                    output = container.logs().decode('utf-8').strip()
                    print("\nDEBUG - Container Output lines:")
                    print("-" * 50)
                    lines = output.split('\n')
                    for i, line in enumerate(lines):
                        print(f"Line {i}: {repr(line)}")
                    print("-" * 50)

                    # Process exit code
                    if result['StatusCode'] != 0:
                        return {"error": "Solution failed with non-zero exit code"}

                    # Look for the last JSON line as our result
                    for line in reversed(lines):
                        line = line.strip()
                        try:
                            result_dict = json.loads(line)
                            print("DEBUG - Successfully parsed JSON:", result_dict)
                            return result_dict
                        except json.JSONDecodeError:
                            continue

                    return {"error": "No valid result found in output"}

                except requests.exceptions.ReadTimeout:
                    return {
                        "error": "Execution timeout - solution took longer than 3 seconds"
                    }
                finally:
                    # Always clean up container
                    try:
                        container.remove(force=True)
                    except Exception as e:
                        print(f"Warning: Failed to remove container: {e}")

            except Exception as e:
                print(f"Container error: {e}")
                return {"error": str(e)}