import arrow
import re

from .helpers import humanize_bytes


class ImageQuery:

    def __init__(self, client):
        self.client = client
        self._imgs_by_id = {}

        for img in self.client.images.list():
            self._imgs_by_id[img.id] = img

    def __iter__(self):
        return self.filter()

    def filter(self, tag=None, min_size=0, min_age=0):
        imgs_by_id = self._imgs_by_id
        tag_pattern = None
        now = arrow.now()

        if isinstance(tag, str):
            tag_pattern = re.compile(r'^%s$' % tag)
        elif hasattr(tag, 'search'):
            tag_pattern = tag

        for img in imgs_by_id.values():
            if tag_pattern and not self._has_tag(img, tag_pattern):
                continue

            created_at = arrow.get(img.attrs['Created'])
            age = (now - created_at).total_seconds()
            age_human = created_at.humanize(other=now, only_distance=True)

            if age < min_age:
                continue

            parent = self._find_parent(img)
            size = self._calc_size(img, parent)
            size_human = humanize_bytes(size)
            tags = sorted(img.tags)
            main_tag = tags[0] if tags else ''

            if size < min_size:
                continue

            yield {
                'id': img.id.replace('sha256:', ''),
                'short_id': img.short_id.replace('sha256:', ''),
                'has_parent': bool(parent),
                'age': age,
                'age_human': age_human,
                'size': size,
                'size_human': size_human,
                'tags': tags,
                'tag': main_tag,
            }

    def _calc_size(self, image, parent):
        parent_size = parent.attrs['Size'] if parent else 0
        return image.attrs['Size'] - parent_size

    def _find_parent(self, image):
        layers = [
            layer for layer in image.history()
            if layer['Id'] != '<missing>' and layer['Id'] != image.id
        ]

        if len(layers) > 0:
            return self._imgs_by_id.get(layers[-1]['Id'])

        return None

    def _has_tag(self, image, pattern):
        return any(pattern.search(tag) for tag in image.tags)
