from pathlib import Path
import os

EMSCRIPTEN_HOME = "/home/web_user"
_THIS_DIR = Path(os.path.dirname(os.path.realpath(__file__)))

JS_DIR = _THIS_DIR / "js"
HTML_DIR = _THIS_DIR / "html"
