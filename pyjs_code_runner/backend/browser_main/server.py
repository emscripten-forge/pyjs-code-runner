import socket
import threading

from contextlib import closing, contextmanager
from http.server import HTTPServer, SimpleHTTPRequestHandler


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def start_server(work_dir, port):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=work_dir, **kwargs)

        def log_message(self, fmt, *args):
            return

    httpd = HTTPServer(("127.0.0.1", port), Handler)

    thread = threading.Thread(target=httpd.serve_forever)
    thread.start()
    return thread, httpd


@contextmanager
def server_context(work_dir, port):
    thread, server = start_server(work_dir=work_dir, port=port)
    try:
        yield server, f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join()
