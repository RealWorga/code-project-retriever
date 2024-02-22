import ast
import os
import sys


def strip_comments_and_docstrings(source):
    """
    Removes comments and docstrings from a Python source file.
    """
    parsed = ast.parse(source)
    for node in ast.walk(parsed):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            node.body = [n for n in node.body if not isinstance(
                n, ast.Expr) or not isinstance(n.value, ast.Constant)]
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            node.value = ast.Constant(s='')
    return parsed


def validate_source(cleaned_source, file_path):
    """
    Ensures that the cleaned source can be parsed by the Python parser.
    """
    try:
        ast.parse(cleaned_source)
    except SyntaxError as e:
        raise ValueError(
            f"Error parsing cleaned source for {file_path}: {e}") from e


def process_file(file_path, remove_newlines=False):
    """
    Processes a non-empty Python file, removing comments and docstrings.
    Returns None if the file is empty.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            source = file.read()
            if not source.strip():
                return None
    except (IOError, PermissionError) as e:
        raise ValueError(f"Error opening {file_path}: {e}") from e

    parsed_ast = strip_comments_and_docstrings(source)
    stripped_source = ast.unparse(parsed_ast)
    if remove_newlines:
        cleaned_source = '\n'.join(
            line.rstrip() for line in stripped_source.splitlines() if line.strip())
    else:
        cleaned_source = '\n'.join(line.rstrip()
                                   for line in stripped_source.splitlines())

    try:
        validate_source(cleaned_source, file_path)
    except SyntaxError as e:
        raise ValueError(
            f"Error parsing cleaned source for {file_path}: {e}") from e

    return cleaned_source


def process_directory(directory_path, target_directory, remove_newlines=False, verbose=False):
    """
    Processes a directory of non-empty Python files, removing comments and docstrings.
    Skips writing files that are detected as empty by process_file.
    """
    for root, _, files in os.walk(directory_path):
        relative_path = os.path.relpath(root, directory_path)
        target_dir = os.path.join(target_directory, relative_path)
        os.makedirs(target_dir, exist_ok=True)
        for file in files:
            if file.endswith('.py'):
                source_file_path = os.path.join(root, file)
                target_file_path = os.path.join(target_dir, file)
                try:
                    stripped_source = process_file(
                        source_file_path, remove_newlines)
                    if stripped_source is not None:
                        with open(target_file_path, 'w', encoding='utf-8') as new_file:
                            new_file.write(stripped_source)
                    elif verbose:
                        print(
                            f"Skipped writing empty or ignored file: {target_file_path}")
                except ValueError as e:
                    if verbose:
                        print(
                            f"Error processing {source_file_path}: {e}", file=sys.stderr)


def handle_cli_args(args):
    """
    Handles the CLI arguments for the comment stripping functionality.
    """
    verbose = args.verbose
    if os.path.isdir(args.path):
        parent_dir = os.path.abspath(os.path.join(args.path, os.pardir))
        dir_basename = os.path.basename(os.path.normpath(args.path))
        target_directory = os.path.join(parent_dir, dir_basename + '_stripped')

        process_directory(args.path, target_directory,
                          remove_newlines=args.remove_newlines, verbose=verbose)
    elif os.path.isfile(args.path):
        cleaned_source = process_file(
            args.path, remove_newlines=args.remove_newlines)
        target_file_path = args.path.rsplit('.', 1)[0] + '_stripped.py'
        with open(target_file_path, 'w', encoding='utf-8') as new_file:
            new_file.write(cleaned_source)
    else:
        raise FileNotFoundError(f"The path {args.path} does not exist.")
    if verbose:
        print(
            f"{args.path} has been processed by the \"comment stripper\" successfully!")
