import pytest
import subprocess
from pathlib import Path
import appdirs
import shutil
from typer.testing import CliRunner
import os

ON_GITHUB_ACTIONS = False
if "GITHUB_ACTION" in os.environ:
    ON_GITHUB_ACTIONS = True


@pytest.fixture(scope="session")
def env_prefix(tmp_path_factory):

    env_root = tmp_path_factory.mktemp("pytest_code_runner_tests")
    env_prefix = Path(env_root) / "testenv"

    if env_prefix.exists():
        shutil.rmtree(env_prefix)

    channels = "-c https://repo.prefix.dev/emscripten-forge/6x -c conda-forge"
    cmd = [
        f"""$MAMBA_EXE create {channels} --yes --prefix {env_prefix} --platform=emscripten-wasm32 python numpy "pyjs-dev>=4.1.0" """
    ]

    ret = subprocess.run(cmd, shell=True)
    #  stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    returncode = ret.returncode
    assert returncode == 0

    return env_prefix


# browsers to test the browser-{main,worker} backends with,
# e.g. PYJS_CODE_RUNNER_TEST_BROWSERS="chromium firefox webkit"
TEST_BROWSERS = os.environ.get("PYJS_CODE_RUNNER_TEST_BROWSERS", "chromium").split()


# @pytest.fixture(params=["node"])  # , "browser-main", "browser-worker"])
@pytest.fixture(
    params=[
        (backend, browser)
        for backend in ["browser-main", "browser-worker"]
        for browser in TEST_BROWSERS
    ],
    ids=lambda p: f"{p[0]}-{p[1]}",
)
def backend_cli_settings(request):
    backend, browser = request.param
    if backend == "node":
        if ON_GITHUB_ACTIONS:
            return backend, [
                "--node-binary",
                "/home/runner/micromamba-root/envs/dev-env/bin/node",
            ]
        else:
            return backend, []
    else:
        return backend, ["--headless", "--browser", browser]


@pytest.fixture
def em_work_dir():
    return Path("/test")


@pytest.fixture
def runner():
    runner = CliRunner()
    return runner
