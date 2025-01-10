#!/usr/bin/env python3
"""
generate_project_md.py
-------
A script to document your Python project by creating a markdown file
with the project structure and all source code included. It also handles
binary files by converting them to hexadecimal representation.

Usage:
    python generate_project_md.py
"""

import os

# You can adjust these lists as needed to exclude or include certain files/folders.
EXCLUDED_DIRS = {'.git', '.idea', '__pycache__', 'venv', '.venv'}
EXCLUDED_FILES = {'generate_project_md.py'}
# Extensions considered as binary files
EXCLUDED_EXTENSIONS = {'.bin', '.txt', '.md'}
BINARY_EXTENSIONS = {'.bin'}

def get_directory_structure(root_dir):
    """
    Recursively get the directory structure as a nested dictionary.

    :param root_dir: The root directory path.
    :return: A dict representing the structure of directories and files:
             {
                "dirname": {
                    "subdir1": { ... },
                    "subdir2": { ... },
                    "files": ["file1.py", "file2.txt", ...]
                }
             }
    """
    structure = {}
    # We store file list separately under the key "files"
    structure["files"] = []

    with os.scandir(root_dir) as entries:
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                # Exclude certain directories
                if entry.name not in EXCLUDED_DIRS and not entry.name.startswith('.'):
                    structure[entry.name] = get_directory_structure(os.path.join(root_dir, entry.name))
            else:
                # If it's a file, decide if we keep it or exclude it
                if entry.name not in EXCLUDED_FILES:
                    structure["files"].append(entry.name)

    return structure

def write_structure_markdown(structure, indent_level=0, current_path=""):
    """
    Recursively write the project structure in a tree-like format.

    :param structure: The nested dictionary with files and folders.
    :param indent_level: Current indentation level for the tree structure.
    :param current_path: The path so far (used in subfolders).
    :return: A string containing the tree representation in markdown.
    """
    md = ""
    # List of files at this level
    files = structure["files"] if "files" in structure else []

    # Sort files alphabetically to keep things neat
    files.sort()
    for f in files:
        md += "  " * indent_level + f"- `{f}`\n"

    # Folders
    for key in sorted(structure.keys()):
        if key not in ("files",):
            # key is a subdirectory
            md += "  " * indent_level + f"- **{key}/**\n"
            md += write_structure_markdown(structure[key], indent_level + 1, os.path.join(current_path, key))

    return md

def gather_code_files(structure, root_dir, current_path=""):
    """
    Recursively gather code (file name + file content) from each file in the structure.
    For binary files, convert their content to hexadecimal.

    :param structure: Nested dictionary of the project structure.
    :param root_dir: The absolute path to the root directory.
    :param current_path: The relative path to the current folder.
    :return: A list of tuples (relative_path, code_content).
    """
    code_files = []
    # Step 1: Gather code from files at this level
    for filename in structure["files"]:
        file_path = os.path.join(root_dir, current_path, filename)
        rel_path = os.path.join(current_path, filename)
        _, extension = os.path.splitext(filename)

        if extension.lower() in EXCLUDED_EXTENSIONS:
            continue

        if extension.lower() in BINARY_EXTENSIONS:
            # Handle binary files by converting to hex
            try:
                with open(file_path, "rb") as f:
                    binary_content = f.read()
                # Convert binary data to uppercase hexadecimal representation without spaces
                content = binary_content.hex().upper()
            except Exception as e:
                content = f"<error reading binary file: {e}>"
        else:
            # Handle text files
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                # For non-binary but non-text files, indicate they are not displayed
                content = "<binary or non-text file: not displayed>"
            except Exception as e:
                content = f"<error reading file: {e}>"

        code_files.append((rel_path, content))

    # Step 2: Recursively gather code from subdirectories
    for key in structure:
        if key not in ("files",):
            sub_code_files = gather_code_files(structure[key], root_dir, os.path.join(current_path, key))
            code_files.extend(sub_code_files)

    return code_files

def main():
    # 1. Get the project structure
    root_dir = os.path.abspath(os.path.dirname(__file__))
    project_structure = get_directory_structure(root_dir)

    # 2. Build the Markdown
    md_content = []
    md_content.append("# Project Documentation\n")
    md_content.append("This document contains the structure of the project and the "
                      "source code for each file.\n")

    # 2a. Add project structure (tree-like)
    md_content.append("## Project Structure\n")
    md_content.append("```\n")
    md_content.append(write_structure_markdown(project_structure))
    md_content.append("```\n")

    # 2b. Add code for each file
    md_content.append("## Source Code\n")
    code_files = gather_code_files(project_structure, root_dir)
    # Sort by filename so we have consistent ordering
    code_files.sort(key=lambda x: x[0].lower())

    for filename, content in code_files:
        _, extension = os.path.splitext(filename)
        # Determine language for syntax highlighting
        if extension.lower() == ".py":
            language = "python"
        elif extension.lower() == ".js":
            language = "javascript"
        elif extension.lower() == ".html":
            language = "html"
        elif extension.lower() == ".css":
            language = "css"
        elif extension.lower() == ".json":
            language = "json"
        elif extension.lower() in BINARY_EXTENSIONS:
            language = ""  # No specific language
        else:
            language = ""

        md_content.append(f"### `{filename}`\n")
        if extension.lower() in BINARY_EXTENSIONS:
            md_content.append("```plaintext\n")
            md_content.append(content)
            md_content.append("\n```\n\n")
        else:
            md_content.append(f"```{language}\n")
            md_content.append(content)
            md_content.append("\n```\n\n")

    # 3. Write the project.md file
    with open(os.path.join(root_dir, "docs/project.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))

if __name__ == "__main__":
    main()
