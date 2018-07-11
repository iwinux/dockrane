from operator import itemgetter
import re

from beautifultable import BeautifulTable
from docker import DockerClient

from dockrane.query import ImageQuery


def print_images_table(images) -> None:
    table = BeautifulTable(150, BeautifulTable.ALIGN_LEFT)
    table.column_headers = ['ID', 'Size', 'Age', 'Tag']
    table.width_exceed_policy = BeautifulTable.WEP_ELLIPSIS
    table.set_style(BeautifulTable.STYLE_COMPACT)
    row_keys = ['short_id', 'size_human', 'age_human']

    for image in images:
        for tag in image['tags']:
            row = [image[key] for key in row_keys]
            row.append(tag)
            table.append_row(row)

    print(table)


OUTPUT_PRINTERS = {
    'table': print_images_table,
}

SORT_KEYS = {'age', 'size', 'tag'}


def run(docker: DockerClient, options: dict) -> None:
    tag = options['tag']

    if options['tag_pattern']:
        tag = re.compile(options['tag_pattern'])

    query = ImageQuery(docker)
    images = query.filter(
        tag=tag, min_size=options['size_gte'], min_age=options['age_gte']
    )

    if options['sort_by'] in SORT_KEYS:
        images = sorted(images, key=itemgetter(options['sort_by']))

    print_output = OUTPUT_PRINTERS.get(options['format'])
    print_output(images)
