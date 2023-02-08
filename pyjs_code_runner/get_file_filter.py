import urllib.request
from pathlib import Path
from empack.file_patterns import pkg_file_filter_from_yaml

from .constants import EMPACK_FILE_FILTER_URL


def get_file_filter(pkg_file_filter, cache_dir):
    if pkg_file_filter is None or len(pkg_file_filter) == 0:

        # empack now supports passing None
        return None
        # path_in_cache = Path(cache_dir) / "empack_config.yaml"
        # if not path_in_cache.exists():

        #     urllib.request.urlretrieve(EMPACK_FILE_FILTER_URL, path_in_cache)
        # return pkg_file_filter_from_yaml(path_in_cache)

    else:
        print(pkg_file_filter)
        return pkg_file_filter_from_yaml(*pkg_file_filter)
