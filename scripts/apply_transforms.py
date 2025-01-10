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