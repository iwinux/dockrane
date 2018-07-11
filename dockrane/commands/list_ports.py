from itertools import chain

from beautifultable import BeautifulTable
from docker import DockerClient


def run(docker: DockerClient) -> None:
    containers = docker.containers.list(all=True)

    table = BeautifulTable(80, BeautifulTable.ALIGN_LEFT)
    table.column_headers = ['ID', 'Name', 'Port']
    table.width_exceed_policy = BeautifulTable.WEP_ELLIPSIS
    table.set_style(BeautifulTable.STYLE_COMPACT)

    for c in containers:
        bindings = c.attrs['HostConfig']['PortBindings']
        if not bindings:
            continue

        for bind in chain.from_iterable(bindings.values()):
            port = '{HostIp}:{HostPort}'.format(**bind)
            table.append_row((c.short_id, c.name, port))

    print(table)
