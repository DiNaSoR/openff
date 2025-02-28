#!/usr/bin/env python3

"""
This script checks for null bytes in Python files that could be causing import errors.
"""

import os
import sys

def check_file(file_path):
    """Check if a file contains null bytes."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            null_positions = [i for i, byte in enumerate(content) if byte == 0]
            return null_positions
    except Exception as e:
        return f"Error reading file: {str(e)}"

def check_directory(directory):
    """Recursively check all Python files in a directory for null bytes."""
    results = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                null_positions = check_file(file_path)
                if null_positions:  # Only add if there are null bytes or errors
                    if isinstance(null_positions, list):
                        if null_positions:  # Only add if the list is not empty
                            results.append((file_path, null_positions))
                    else:  # It's an error message
                        results.append((file_path, null_positions))
    return results

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "editor"
    
    print(f"Checking directory: {directory}")
    results = check_directory(directory)
    
    if not results:
        print("No null bytes found in any Python files.")
    else:
        print(f"Found {len(results)} files with null bytes or errors:")
        for file_path, positions in results:
            if isinstance(positions, list):
                print(f"- {file_path}: {len(positions)} null bytes at positions {positions[:5]}{'...' if len(positions) > 5 else ''}")
            else:
                print(f"- {file_path}: {positions}")

if __name__ == "__main__":
    main() 