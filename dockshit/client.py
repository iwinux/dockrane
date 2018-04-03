import re

import arrow
import docker

from .helpers import calc_size, has_tag, humanize_bytes


class ImageQuery:

    def __init__(self, client):
        self.client = client
        self._imgs_by_id = {}

        for img in self.client.images.list():
            self._imgs_by_id[img.id] = img

    def filter(self, tag=None, min_size=0, min_age=0):
        imgs_by_id = self._imgs_by_id
        tag_pattern = None
        now = arrow.now()
        selected = []

        if isinstance(tag, str):
            tag_pattern = re.compile(r'^%s$' % tag)
        elif hasattr(tag, 'search'):
            tag_pattern = tag

        for img in imgs_by_id.values():
            if tag_pattern and not has_tag(img, tag_pattern):
                continue

            attrs = img.attrs
            created_at = arrow.get(attrs['Created'])
            age = (now - created_at).total_seconds()

            if age < min_age:
                continue

            age_human = created_at.humanize(other=now, only_distance=True)
            parent = imgs_by_id.get(attrs['Parent'])
            n_bytes = calc_size(img, parent)

            if n_bytes < min_size:
                continue

            selected.append(
                {
                    'id': img.id.replace('sha256:', ''),
                    'instance': img,
                    'has_parent': bool(parent),
                    'age': age,
                    'age_human': age_human,
                    'size': n_bytes,
                    'size_human': humanize_bytes(n_bytes),
                    'tags': img.tags,
                }
            )

        return selected


class DockShit:

    def __init__(self, api_version='auto', **client_args):
        self.client = docker.from_env(version=api_version, **client_args)

    def list_images(self):
        return ImageQuery(self.client)
