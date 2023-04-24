from enum import Enum
import textwrap


class BackendFamilyType(str, Enum):
    browser = "browser"
    node = "node"


class BackendType(str, Enum):
    browser_main = "browser-main"
    browser_worker = "browser-worker"
    node = "node"


def get_backend_type_family(backend):
    if backend == BackendType.node:
        return BackendFamilyType.node
    else:
        return BackendFamilyType.browser


def ensure_playwright_imports():
    try:
        import playwright
    except ModuleNotFoundError as e:
        msg = """\n
            pyjs-code-runner error: 

                * Cannot import playwright!

            To use the browser-{worker/main} backends `playwright` needs to be installed.

            Install playwight with:

                * conda:

                    conda install -c microsoft playwright
                    playwright install

                * mamba:

                    mamba install -c microsoft playwright
                    playwright install

                * micromamba:

                    micromamb install -c microsoft playwright
                    playwright install

                * pip:

                    python -m pip install playwright
                    playwright install



        """
        raise ModuleNotFoundError(textwrap.dedent(msg))


def get_backend_cls(backend_type):
    if backend_type == BackendType.node:
        raise RuntimeError(
            "the node backend is currently disabled as its not (yet) working with empack>=3.0.0"
        )

    elif backend_type == BackendType.browser_main:
        ensure_playwright_imports()
        from .browser_main.browser_main import BrowserMainBackend

        return BrowserMainBackend
    elif backend_type == BackendType.browser_worker:
        ensure_playwright_imports()
        from .browser_worker.browser_worker import BrowserWorkerBackend

        return BrowserWorkerBackend
