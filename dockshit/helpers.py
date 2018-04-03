UNIT_GB = 1024 ** 3
UNIT_MB = 1024 ** 2
UNIT_KB = 1024


def calc_size(image, parent):
    parent_size = parent.attrs['Size'] if parent else 0
    return image.attrs['Size'] - parent_size


def humanize_bytes(n_bytes):
    if (n_bytes // UNIT_GB) >= 1:
        return '%.2fGB' % (n_bytes / UNIT_GB)
    elif (n_bytes // UNIT_MB) >= 1:
        return '%.2fMB' % (n_bytes / UNIT_MB)
    else:
        return '%.2fKB' % (n_bytes / UNIT_KB)


def has_tag(image, pattern):
    return any(pattern.search(tag) for tag in image.tags)
