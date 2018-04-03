from argparse import ArgumentParser
from operator import itemgetter
import re
import sys

from beautifultable import BeautifulTable

from .client import get_docker_client
from .query import ImageQuery


def print_images_table(images):
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


def main(args):
    tag = args.tag
    if args.tag_pattern:
        tag = re.compile(args.tag_pattern)

    client = get_docker_client()
    query = ImageQuery(client)
    images = query.filter(tag=tag, min_size=args.size_gte, min_age=args.age_gte)

    if args.sort_by in SORT_KEYS:
        images = sorted(images, key=itemgetter(args.sort_by))

    print_output = OUTPUT_PRINTERS.get(args.format)
    print_output(images)
    client.close()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--format', default='table')
    parser.add_argument('--sort-by', default='tag')
    parser.add_argument('--age-gte', type=int, default=0)
    parser.add_argument('--size-gte', type=int, default=0)
    parser.add_argument('-t', '--tag')
    parser.add_argument('--tag-pattern')
    main(parser.parse_args(sys.argv[1:]))
