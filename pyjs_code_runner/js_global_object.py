from .backend.backend import BackendType


def js_global_object(backend_type):
    if backend_type == BackendType.node:
        return "global"
    else:
        return "globalThis"
