#!/usr/bin/env python3
"""Script to fix common lint issues"""
import re
import glob


def fix_trailing_whitespace(content):
    """Remove trailing whitespace from each line"""
    lines = content.split('\n')
    fixed_lines = [line.rstrip() for line in lines]
    return '\n'.join(fixed_lines)


def fix_comparison_to_false(content):
    """Fix comparison to False - use 'is False' or 'not'"""
    # Pattern: is False -> is False
    content = re.sub(r'([^\s])(\s*)==\s*False', r'\1 is False', content)
    # Pattern: is not False -> is not False
    content = re.sub(r'([^\s])(\s*)!=\s*False', r'\1 is not False', content)
    return content


def fix_arithmetic_operator_spacing(content):
    """Add whitespace around arithmetic operators"""
    # Fix cases like n * 2 -> n * 2, but avoid ** (power operator)
    content = re.sub(r'(\w)(\*{1})(\d)', r'\1 * \3', content)
    content = re.sub(r'(\w)(/)(\d)', r'\1 / \3', content)
    content = re.sub(r'(\w)(\+)(\d)', r'\1 + \3', content)
    content = re.sub(r'(\w)(-)(\d)', r'\1 - \3', content)
    return content


def process_file(filepath):
    """Process a single Python file"""
    try:
        with open(filepath, 'r', encoding='utf - 8') as f:
            content = f.read()

        original = content

        # Apply fixes
        content = fix_trailing_whitespace(content)
        content = fix_comparison_to_false(content)
        content = fix_arithmetic_operator_spacing(content)

        # Only write if changes were made
        if content != original:
            with open(filepath, 'w', encoding='utf - 8') as f:
                f.write(content)
            print(f"Fixed: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    """Main function"""
    # Get all Python files in root and agents directory
    python_files = []
    python_files.extend(glob.glob('*.py'))
    python_files.extend(glob.glob('agents/*.py'))

    fixed_count = 0
    for filepath in python_files:
        if process_file(filepath):
            fixed_count += 1

    print(f"\nTotal files fixed: {fixed_count}")


if __name__ == '__main__':
    main()
