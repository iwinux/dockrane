import posixpath
import sys

from docker import DockerClient
from docker.errors import ImageNotFound
from progress.bar import Bar


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


def run(docker: DockerClient, options: dict) -> None:
    src_name, src_tag = split_tag(options['src'], strip_namespace=True)

    if options['dest']:
        dest_name, dest_tag = split_tag(
            options['dest'], strip_namespace=bool(options['namespace'])
        )
    else:
        dest_name = src_name
        dest_tag = src_tag

    dest_repo = posixpath.join(options['namespace'], dest_name)
    dest = '{repo}:{tag}'.format(repo=dest_repo, tag=dest_tag)

    print('Source: {src}'.format(src=options['src']))
    print('Dest: {dest}'.format(dest=dest))

    if options['dry_run']:
        return

    try:
        image = docker.images.get(options['src'])
    except ImageNotFound:
        if options['pull']:
            src_repo, _ = split_tag(options['src'])
            image = pull_image(docker, options['src'])
        else:
            sys.exit('image `%s` not found' % options['src'])

    image.tag(dest_repo, dest_tag)

    if options['push']:
        try:
            push_image(docker, dest_repo, dest_tag)
            print('Pushed {dest}'.format(dest=dest))
        except KeyboardInterrupt:
            pass
