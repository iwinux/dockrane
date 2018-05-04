from argparse import ArgumentParser
import sys

from .commands import list_host_ports
from .commands import list_images
from .commands import transfer_image

SUB_COMMANDS = [list_host_ports, list_images, transfer_image]


def main():
    parser = ArgumentParser()
    commands = parser.add_subparsers(dest='command')

    for c in SUB_COMMANDS:
        c.register(commands)

    args = parser.parse_args(sys.argv[1:])
    command = getattr(args, 'command', None)

    if command:
        args.command(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
