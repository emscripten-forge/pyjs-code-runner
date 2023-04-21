import appdirs

from pathlib import Path


def get_appdir():
    path = Path(appdirs.user_data_dir("pyjs_code_runner", "ThorstenBeier"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cache_dir(cache_dir=None):
    if cache_dir is None:
        return get_appdir()
    else:
        return Path(cache_dir)
