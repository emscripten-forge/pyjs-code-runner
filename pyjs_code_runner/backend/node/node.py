import subprocess
from pathlib import Path
import os
import shutil
import sys

from ..backend_base import BackendBase

THIS_DIR = os.path.dirname(os.path.realpath(__file__))


class NodeBackend(BackendBase):
    def __init__(self, host_work_dir, work_dir, script, async_main, node_exe):
        super().__init__(
            host_work_dir=host_work_dir,
            work_dir=work_dir,
            script=script,
            async_main=async_main,
        )

        self.node_exe = node_exe

    def run(self):
        print("run in node", self.script, self.node_exe, "CWD", os.getcwd())

        main_name = "node_main.js"
        main = Path(THIS_DIR) / main_name
        shutil.copyfile(main, self.host_work_dir / main_name)

        cmd = [
            "node",
            "--no-experimental-fetch",
            main_name,
            self.work_dir,
            self.script,
            str(int(self.async_main)),
        ]

        returncode = subprocess.run(cmd, cwd=os.getcwd()).returncode
        if returncode != 0:
            sys.exit(returncode)
