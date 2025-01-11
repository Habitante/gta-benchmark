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
    for i in range(1, 25):
        filepath = os.path.join(shared_directory, f'visible_{i:02d}.bin')
        with open(filepath, 'rb') as f:
            buf = f.read()
            visible_buffers.append(buf)
            seen_bytes.update(buf)

    missing_bytes = set(range(256)) - seen_bytes

    # Load hidden buffers and check which ones contain missing bytes
    hidden_with_missing = 0
    for i in range(1, 25):  # Changed to 24 buffers
        filepath = os.path.join(shared_directory, f'hidden_{i:02d}.bin')
        with open(filepath, 'rb') as f:
            buf = f.read()
            hidden_buffers.append(buf)
            # Check if this buffer has any of the missing bytes
            if any(byte in missing_bytes for byte in buf):
                hidden_with_missing += 1
            else:
                print(f"\nHidden buffer #{i} contains no missing bytes!")

    print(f"\nNumber of hidden buffers containing missing bytes: {hidden_with_missing} out of 24")

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

    prompt += """
Instructions:
- Return just your best possible approximation as a small python function that takes a 64 byte array as input, and returns the 64 byte array as output. 
- Remember, the transformation is the same for all 24 buffers.
- The function will be scored by the number of buffers that are correctly transformed (as shown in the 24 outputs).
- And it also will be tested on another set of 24 hidden input buffers not shown in the prompt. 
- Do not include anything else in your response, no introduction text or explanations.

Example Output:
def transform(data: bytes) -> bytes:
   # Transform logic
   return bytes"""

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


def output_transformed_buffers(root_dir='../puzzles'):
    """
    Generate a single document with all transforms outputs.
    """
    visible_buffers, hidden_buffers = load_all_buffers()
    all_outputs = []

    # Walk through all subdirectories in sorted order
    for root, dirs, files in sorted(os.walk(root_dir)):
        # Look for transform_*.py files
        for file in sorted(files):
            if file.startswith('transform_') and file.endswith('.py'):
                transform_file = os.path.join(root, file)

                # Extract level and puzzle numbers from path
                parts = transform_file.split(os.sep)
                if len(parts) >= 3:
                    level_dir = parts[-2]  # e.g. 'level_1'
                    puzzle_num = file.split('_')[1].split('.')[0]  # Extract number from transform_N.py

                    try:
                        # Load the transform function
                        transform = load_transform(transform_file)

                        # Apply transform to visible buffers
                        outputs = []
                        for buf in visible_buffers:
                            output = transform(buf)
                            outputs.append(output.hex())

                        # Format the output
                        header = f"\nLevel {level_dir[-1]}-{puzzle_num}\n"
                        out_lines = [f"OUTPUT #{i + 1:02d}: {out}" for i, out in enumerate(outputs)]

                        all_outputs.append(header + "\n".join(out_lines))

                        print(f"Processed transform for {level_dir}-{puzzle_num}")

                    except Exception as e:
                        print(f"Error applying transform for {transform_file}: {e}")

    # Save combined output
    with open('all_transforms_output.txt', 'w') as f:
        f.write("\n".join(all_outputs))
    print("Generated combined output file: all_transforms_output.txt")

if __name__ == "__main__":
    #output_transformed_buffers()
    apply_and_save_transforms()
