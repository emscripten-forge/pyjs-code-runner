import pytest
import subprocess
from pathlib import Path
import shutil
from typer.testing import CliRunner
import os

ON_GITHUB_ACTIONS = False
if "GITHUB_ACTION" in os.environ:
    ON_GITHUB_ACTIONS = True


# Where pyjs comes from in the tests:
#   npm   (default, the CI): the published npm package PYJS_CODE_RUNNER_TEST_NPM
#   conda (local, `pixi run test-conda`): an emscripten-forge env with
#         pyjs-dev >= 6, e.g. from a local recipe build
#         (PYJS_CODE_RUNNER_TEST_CHANNEL)
TEST_MODE = os.environ.get("PYJS_CODE_RUNNER_TEST_MODE", "npm")
TEST_NPM = os.environ.get("PYJS_CODE_RUNNER_TEST_NPM", "@derthorsten/pyjs@6.0.1")


@pytest.fixture(scope="session")
def pyjs_args(request):
    """the CLI arguments that say where pyjs comes from (see TEST_MODE)"""
    if TEST_MODE == "npm":
        return ["--pyjs-npm", TEST_NPM]
    if TEST_MODE == "conda":
        return ["--conda-env", request.getfixturevalue("env_prefix")]
    raise ValueError(f"PYJS_CODE_RUNNER_TEST_MODE: npm or conda, not {TEST_MODE!r}")


@pytest.fixture(scope="session")
def env_prefix(tmp_path_factory):

    env_root = tmp_path_factory.mktemp("pytest_code_runner_tests")
    env_prefix = Path(env_root) / "testenv"

    if env_prefix.exists():
        shutil.rmtree(env_prefix)

    channels = "-c https://repo.prefix.dev/emscripten-forge/6x -c conda-forge"
    # e.g. a local recipe build output with a freshly built pyjs, searched first
    local_channel = os.environ.get("PYJS_CODE_RUNNER_TEST_CHANNEL")
    if local_channel:
        channels = f"-c {local_channel} {channels}"
    # (pyjs >= 6: its conda package ships the npm JavaScript the runner needs)
    # micromamba of the pixi env (or the one of setup-micromamba)
    mamba = os.environ.get("MAMBA_EXE", "micromamba")
    cmd = [
        f"""{mamba} create {channels} --yes --prefix {env_prefix} --platform=emscripten-wasm32 python numpy "pyjs-dev>=6" """
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
