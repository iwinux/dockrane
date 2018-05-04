import json
import posixpath
import sys

from docker.errors import ImageNotFound
from progress.bar import Bar

from dockshit.client import get_docker_client


def parse_suffix(name):
    suffix_parts = posixpath.basename(name).split(':')

    if len(suffix_parts) == 2:
        name, tag = suffix_parts
    else:
        name, = suffix_parts
        tag = 'latest'

    return name, tag


def run(args) -> None:
    src_name, src_tag = parse_suffix(args.src)

    if args.dest:
        dest_name, dest_tag = parse_suffix(args.dest)
    else:
        dest_name = src_name
        dest_tag = src_tag

    dest_repo = posixpath.join(args.namespace, dest_name)
    dest = '{repo}:{tag}'.format(repo=dest_repo, tag=dest_tag)

    print('Source: {src}'.format(src=args.src))
    print('Dest: {dest}'.format(dest=dest))

    if args.dry_run:
        return

    client = get_docker_client()

    try:
        image = client.images.get(args.src)
    except ImageNotFound:
        sys.exit('image `%s` not found' % args.src)

    image.tag(dest_repo, dest_tag)

    if args.push:
        bar = Bar()

        try:
            print('')
            rv = client.images.push(dest_repo, dest_tag, stream=True)

            for line in rv:
                result = json.loads(line.decode('utf-8'))
                status = result.get('status')

                if 'id' in result:
                    if status == 'Pushing':
                        output = '{id}: {status} {progress}'.format(**result)
                        bar.writeln(output)
                    elif status == 'Pushed':
                        bar.clearln()
                        print('{id}: {status}'.format(**result))
                    else:
                        print('{id}: {status}'.format(**result))

            bar.finish()
            bar.clearln()
            print('Pushed {dest}'.format(dest=dest))
        except KeyboardInterrupt:
            pass

    client.close()


def register(commands) -> None:
    parser = commands.add_parser('transfer-image')
    parser.add_argument('src')
    parser.add_argument('dest', nargs='?', default='')
    parser.add_argument('--dry-run', action='store_true', default=False)
    parser.add_argument('--namespace', default='')
    parser.add_argument('--pull', action='store_true', default=False)
    parser.add_argument('--push', action='store_true', default=False)
    parser.set_defaults(command=run)
