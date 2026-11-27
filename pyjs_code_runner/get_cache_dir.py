import os
from pathlib import Path


def get_appdir():
    """the default cache directory: $XDG_CACHE_HOME/pyjs_code_runner, else
    ~/.cache/pyjs_code_runner"""
    root = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    path = Path(root) / "pyjs_code_runner"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cache_dir(cache_dir=None):
    if cache_dir is None:
        return get_appdir()
    else:
        return Path(cache_dir)
