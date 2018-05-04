from argparse import ArgumentParser
import sys

from .commands import list_host_ports
from .commands import list_images

COMMANDS = [list_host_ports, list_images]


def main():
    parser = ArgumentParser()
    commands = parser.add_subparsers(dest='command')

    for c in COMMANDS:
        c.add_command(commands)

    args = parser.parse_args(sys.argv[1:])
    command = getattr(args, 'command', None)

    if command:
        args.command(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
