from empack.file_patterns import pkg_file_filter_from_yaml


def get_file_filter(pkg_file_filter):
    if pkg_file_filter is None or len(pkg_file_filter) == 0:
        return None
    else:
        print(pkg_file_filter)
        return pkg_file_filter_from_yaml(*pkg_file_filter)
