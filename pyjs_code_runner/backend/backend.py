from enum import Enum

from .node.node import NodeBackend
from .browser_main.browser_main import BrowserMainBackend
from .browser_worker.browser_worker import BrowserWorkerBackend


class BackendFamilyType(str, Enum):
    browser = "browsef"
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


def get_backend_cls(backend_type):
    if backend_type == BackendType.node:
        return NodeBackend
    elif backend_type == BackendType.browser_main:
        return BrowserMainBackend
    elif backend_type == BackendType.browser_worker:
        return BrowserWorkerBackend
