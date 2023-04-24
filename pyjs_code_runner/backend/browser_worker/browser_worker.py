import os
import asyncio
from ..backend_base import BackendBase
from ...constants import JS_DIR, HTML_DIR
from ..browser_main.server import server_context, find_free_port
from playwright.async_api import async_playwright
from pathlib import Path
import shutil


class BrowserWorkerBackend(BackendBase):
    def __init__(
        self, host_work_dir, work_dir, script, async_main, port, headless, slow_mo
    ):
        super().__init__(
            host_work_dir=host_work_dir,
            work_dir=work_dir,
            script=script,
            async_main=async_main,
        )
        if port is None:
            port = find_free_port()
        self.port = port
        self.headless = headless
        self.slow_mo = slow_mo

    def run(self):
        # copy html
        browser_worker_html = "browser_worker.html"
        main = HTML_DIR / browser_worker_html
        shutil.copyfile(main, self.host_work_dir / browser_worker_html)

        # copy worker
        worker_js = "worker.js"
        main = JS_DIR / worker_js
        shutil.copyfile(main, self.host_work_dir / worker_js)

        with server_context(work_dir=self.host_work_dir, port=self.port) as (
            server,
            url,
        ):
            page_url = f"{url}/{browser_worker_html}"
            ret = asyncio.run(self.playwright_run_in_worker_thread(page_url=page_url))
            if ret != 0:
                raise RuntimeError("return_code != 0")

    async def playwright_run_in_worker_thread(self, page_url):
        async with async_playwright() as p:
            if self.slow_mo is None:
                browser = await p.chromium.launch(headless=self.headless)
            else:
                browser = await p.chromium.launch(
                    headless=self.headless, slow_mo=self.slow_mo
                )
            page = await browser.new_page()

            # n min = n_min * 60 * 1000 ms
            n_min = 4
            page.set_default_timeout(n_min * 60 * 1000)

            async def handle_worker(worker):
                test_output = await worker.evaluate_handle(
                    f"""async () =>
                {{

                    {self.js_utils()}

                    var collected_prints = ""
                    const print = (text) => {{
                        console.log(text)
                        collected_prints += text;
                        collected_prints += "\\n";
                    }}


                    var pyjs = await make_pyjs(print, print);

                    var r = eval_main_script(pyjs, "{self.work_dir}","{self.script}");
                    if({int(self.async_main)}){{
                        r = r || await run_async_python_main(pyjs);
                    }}

                    msg = {{
                        return_code : r,
                        collected_prints : collected_prints
                    }}
                    self.postMessage(msg)
                    return r
                }}"""
                )
                if int(str(test_output)) != 0:
                    raise RuntimeError(f"tests failed with return code: {test_output}")

            page.on("worker", handle_worker)

            async def handle_console(msg):
                txt = str(msg)
                if txt.startswith(
                    "warning: Browser does not support creating object URLs"
                ):
                    pass
                else:
                    print(txt)

            page.on("console", handle_console)
            await page.goto(page_url)
            await page.wait_for_function("() => globalThis.done")

            test_output = await page.evaluate_handle(
                """
                () =>
                {
                return globalThis.test_output
                }
            """
            )
            return_code = int(str(await test_output.get_property("return_code")))
        return return_code
