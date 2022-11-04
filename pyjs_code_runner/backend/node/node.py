import subprocess
from pathlib import Path
import os
import shutil
import json
import sys
import shutil
from ..backend_base import BackendBase
from subprocess import Popen, PIPE, STDOUT
import textwrap

THIS_DIR = os.path.dirname(os.path.realpath(__file__))


class NodeBackend(BackendBase):
    def __init__(self, host_work_dir, work_dir, script, async_main, node_binary):
        super().__init__(
            host_work_dir=host_work_dir,
            work_dir=work_dir,
            script=script,
            async_main=async_main,
        )
        if node_binary is None:
            shutil_node_binary = shutil.which("node")
            if shutil_node_binary is None:
                raise RuntimeError(
                    textwrap.dedent(
                        """\n
                    pyjs-code-runner error: 

                        * Cannot find node


                    to use the node backend `node`/`nodejs` needs to be installed.

                    Install playwight with:

                        * conda:

                            conda install -c conda-forge nodejs

                        * mamba:

                            mamba install -c conda-forge nodejs

                        * micromamba:

                            micromamb install -c conda-forge nodejs

                """
                    )
                )
            else:
                node_binary = shutil_node_binary
        self.node_binary = node_binary

    def supports_flag_no_experimental_fetch(self):
        probe_cmd = [self.node_binary, "--no-experimental-fetch", "--version"]
        ret_code = subprocess.call(
            probe_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return ret_code == 0

    def run(self):
        main_name = "node_main.js"
        main = Path(THIS_DIR) / main_name
        shutil.copyfile(main, self.host_work_dir / main_name)

        cmd = [self.node_binary]
        if self.supports_flag_no_experimental_fetch():
            cmd.append("--no-experimental-fetch")

        cmd.extend(
            [
                main_name,
                self.work_dir,
                self.script,
                str(int(self.async_main)),
                self.host_work_dir,
            ]
        )

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        # Poll process.stdout to show stdout live
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                print(output.decode().strip())
        rc = process.poll()
        if process.returncode != 0:
            raise RuntimeError(
                f"node return with returncode: {process.returncode} rc {rc}"
            )

        result_path = self.host_work_dir / "_node_result.json"
        if result_path.exists():
            with open(result_path, "r") as f:
                results = json.load(f)
            if results["return_code"] != 0:
                raise RuntimeError(results["error"])
        else:
            raise RuntimeError("internal error in pyjs-code-runner")
