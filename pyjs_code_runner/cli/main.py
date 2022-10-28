from .app import app
from .run import *  # noqa: F401, F403
from .version import *  # noqa: F401, F403

if __name__ == "__main__":
    from rich.console import Console

    err_console = Console(stderr=True)
    app(show_locals=False)
