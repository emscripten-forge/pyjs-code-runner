import subprocess
from pathlib import Path
import os
import shutil
import sys

from ..backend_base import BackendBase
from subprocess import Popen, PIPE, STDOUT

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

        if False:
            ret = subprocess.run(cmd, cwd=os.getcwd(), stdout=PIPE)
            returncode = ret.returncode
            output = ret.stdout.decode()
            print(output)
            if returncode != 0:
                sys.exit(returncode)

        else:
            print("START")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

            # Poll process.stdout to show stdout live
            while True:
                output = process.stdout.readline()
                if process.poll() is not None:
                    break
                if output:
                    print(output.decode().strip())
            rc = process.poll()
            # print("RC", rc)
            if process.returncode != 0:
                sys.exit(process.returncode)
