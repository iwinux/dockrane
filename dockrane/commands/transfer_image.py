import posixpath
import sys

from docker.errors import ImageNotFound
from progress.bar import Bar

from dockrane.client import get_docker_client


def split_tag(name, strip_namespace=False):
    if strip_namespace:
        name = posixpath.basename(name)

    suffix_parts = name.split(':')

    if len(suffix_parts) == 2:
        name, tag = suffix_parts
    else:
        name, = suffix_parts
        tag = 'latest'

    return name, tag


def pull_image(client, src):
    src_repo, src_tag = split_tag(src)
    bar = Bar()
    results = client.api.pull(src_repo, src_tag, stream=True, decode=True)

    print('')

    for result in results:
        status = result.get('status')

        if 'id' in result:
            if status == 'Downloading' or status == 'Extracting':
                output = '{id}: {status} {progress}'.format(**result)
                bar.writeln(output)
            elif status == 'Download complete' or status == 'Pull complete':
                bar.clearln()
                print('{id}: {status}'.format(**result))

    bar.finish()
    bar.clearln()

    return client.images.get(src)


def push_image(client, dest_repo, dest_tag):
    bar = Bar()
    results = client.images.push(dest_repo, dest_tag, stream=True, decode=True)

    print('')

    for result in results:
        status = result.get('status')

        if 'id' in result:
            if status == 'Pushing':
                output = '{id}: {status} {progress}'.format(**result)
                bar.writeln(output)
            elif status == 'Pushed':
                bar.clearln()
                print('{id}: {status}'.format(**result))

    bar.finish()
    bar.clearln()


def run(args) -> None:
    src_name, src_tag = split_tag(args.src, strip_namespace=True)

    if args.dest:
        dest_name, dest_tag = split_tag(
            args.dest, strip_namespace=bool(args.namespace)
        )
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
        if args.pull:
            src_repo, _ = split_tag(args.src)
            image = pull_image(client, args.src)
        else:
            sys.exit('image `%s` not found' % args.src)

    image.tag(dest_repo, dest_tag)

    if args.push:
        try:
            push_image(client, dest_repo, dest_tag)
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
