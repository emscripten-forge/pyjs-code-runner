from ..constants import JS_DIR, HTML_DIR


class BackendBase(object):
    def __init__(self, host_work_dir, work_dir, script, async_main):
        self.host_work_dir = host_work_dir
        self.script = script
        self.work_dir = work_dir
        self.async_main = async_main

    def js_utils(self):
        with open(JS_DIR / "utils.js") as f:
            content = f.read()

            return content
