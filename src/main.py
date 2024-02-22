import argparse

# pylint: disable=import-error
from comment_stripper import stripper


def main():
    parser = argparse.ArgumentParser(description='Project Code Retriever CLI')
    subparsers = parser.add_subparsers(help='sub-command help')

    # Subparser for stripping comments & docstrings
    parser_strip = subparsers.add_parser(
        'strip-comments', help='Strip comments and docstrings from Python files')
    parser_strip.add_argument(
        'path', type=str, help='File or directory path to process')
    parser_strip.add_argument(
        '--remove-newlines', action='store_true', help='Remove unnecessary new lines')
    parser_strip.add_argument(
        '--verbose', action='store_true', help='Enable verbose output')
    parser_strip.set_defaults(func=stripper.handle_cli_args)

    args = parser.parse_args()

    # Check if sub-command was provided
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
