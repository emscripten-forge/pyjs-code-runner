"""Run the prepared directory (see run.py) in a browser with playwright: serve
it, open index.html (main thread) or index.html?worker (web worker), print
what the page prints, and wait for its result."""

import asyncio
import json
import socket
import threading
from contextlib import closing, contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.async_api import async_playwright

from .backend import BrowserType, launch_browser

# how long the page may take (also the timeout of every playwright call that
# waits); recipes with long test suites raise it by patching
# Page.set_default_timeout
TIMEOUT_MS = 4 * 60 * 1000


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@contextmanager
def serve(directory, port):
    """serve `directory` at http://127.0.0.1:<port> while in the context"""

    class Handler(SimpleHTTPRequestHandler):
        # (ES modules / module workers need a JavaScript mime type)
        extensions_map = {
            **SimpleHTTPRequestHandler.extensions_map,
            ".js": "text/javascript",
            ".mjs": "text/javascript",
            ".wasm": "application/wasm",
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, fmt, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join()


class BrowserBackend:
    """runs the script in the page's main thread (`worker` False) or in a web
    worker"""

    worker = False

    def __init__(
        self,
        host_work_dir,
        port=None,
        headless=True,
        slow_mo=None,
        browser=BrowserType.chromium,
    ):
        self.host_work_dir = host_work_dir
        self.port = port if port is not None else find_free_port()
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser = BrowserType(browser)

    def run(self):
        with serve(self.host_work_dir, self.port) as url:
            page_url = f"{url}/index.html" + ("?worker" if self.worker else "")
            result = asyncio.run(self._run(page_url))
        if "error" in result:
            raise RuntimeError(f"pyjs-code-runner: {result['error']}")
        if result["code"] != 0:
            raise RuntimeError(f"return_code != 0 ({result['code']})")

    async def _run(self, page_url):
        async with async_playwright() as p:
            browser = await launch_browser(p, self.browser, headless=self.headless, slow_mo=self.slow_mo)
            try:
                page = await browser.new_page()
                page.set_default_timeout(TIMEOUT_MS)
                page.on("console", lambda message: print(message.text, flush=True))
                page.on("pageerror", lambda error: print(f"page error: {error}", flush=True))
                await page.goto(page_url)
                # (the page sets globalThis.result: {code} or {error})
                await page.wait_for_function("() => globalThis.result !== undefined", polling=200)
                return json.loads(await page.evaluate("() => JSON.stringify(globalThis.result)"))
            finally:
                await browser.close()


class BrowserMainBackend(BrowserBackend):
    worker = False


class BrowserWorkerBackend(BrowserBackend):
    worker = True
