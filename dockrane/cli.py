from docker import DockerClient, from_env
import click

from .commands import list_images, list_ports, transfer_image


def get_docker_client(
    api_version: str = 'auto', **client_args: dict
) -> DockerClient:
    return from_env(version=api_version, **client_args)


@click.group()
@click.pass_context
def main(ctx: click.Context) -> None:
    docker = get_docker_client()
    ctx.obj = docker
    ctx.call_on_close(docker.close)


@main.command(name='list-ports', help='list published containers ports')
@click.pass_obj
def cmd_list_ports(docker: DockerClient) -> None:
    list_ports.run(docker)


@main.command(name='list-images', help='list images')
@click.option('-f', '--format', default='table')
@click.option('--sort-by', default='tag')
@click.option('--age-gte', type=int, default=0)
@click.option('--size-gte', type=int, default=0)
@click.option('-t', '--tag')
@click.option('--tag-pattern')
@click.pass_obj
def cmd_list_images(docker: DockerClient, **options: dict) -> None:
    list_images.run(docker, options)


@main.command(name='transfer', help='transfer image')
@click.argument('src')
@click.argument('dest', nargs=-1, required=True)
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--namespace', default='')
@click.option('--pull', is_flag=True, default=False)
@click.option('--push', is_flag=True, default=False)
def cmd_transfer(docker: DockerClient, **options: dict) -> None:
    transfer_image.run(docker, options)


if __name__ == '__main__':
    main()
