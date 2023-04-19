import urllib.request
from pathlib import Path
from empack.file_patterns import pkg_file_filter_from_yaml

from .constants import EMPACK_FILE_FILTER_URL


def get_file_filter(pkg_file_filter, cache_dir):
    if pkg_file_filter is None or len(pkg_file_filter) == 0:
        return None
    else:
        print(pkg_file_filter)
        return pkg_file_filter_from_yaml(*pkg_file_filter)
