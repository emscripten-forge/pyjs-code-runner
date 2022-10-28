from pathlib import Path
import os

EXPORT_NAME_SUFFIX = "EmscriptenForgeModule"
EMSCRIPTEN_HOME = "/home/web_user"
EMPACK_FILE_FILTER_URL = (
    "https://raw.githubusercontent.com/emscripten-forge/recipes/main/empack_config.yaml"
)


_THIS_DIR = Path(os.path.dirname(os.path.realpath(__file__)))

JS_DIR = _THIS_DIR / "js"
HTML_DIR = _THIS_DIR / "html"
