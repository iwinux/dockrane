from argparse import ArgumentParser
import sys

from .commands import list_images

if __name__ == '__main__':
    parser = ArgumentParser()
    commands = parser.add_subparsers(dest='command')
    list_images.add_command(commands)
    args = parser.parse_args(sys.argv[1:])
    command = getattr(args, 'command', None)

    if command:
        args.command(args)
    else:
        parser.print_help()
