import pytest
import subprocess
from pathlib import Path
import appdirs
import shutil
from typer.testing import CliRunner
import os

# @pytest.fixture(scope="session")
# def session_temp_path(tmp_path_factory):
#     return tmp_path_factory.mktemp()

ON_GITHUB_ACTIONS = False
if "GITHUB_ACTION" in os.environ:
    ON_GITHUB_ACTIONS = True


@pytest.fixture(scope="session")
def env_prefix():
    env_root = Path(appdirs.user_data_dir("pytest_code_runner_tests", "DerThorsten"))
    env_root.mkdir(exist_ok=True, parents=True)
    env_prefix = Path(env_root) / "testenv"

    if env_prefix.exists():
        shutil.rmtree(env_prefix)

    print("prefix", env_prefix)
    channels = (
        "-c https://repo.mamba.pm/emscripten-forge -c https://repo.mamba.pm/conda-forge"
    )
    cmd = [
        f"""$MAMBA_EXE create {channels} --yes --prefix {env_prefix} --platform=emscripten-32   python numpy pyjs """
    ]

    ret = subprocess.run(cmd, shell=True)
    #  stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    returncode = ret.returncode
    assert returncode == 0

    return env_prefix


# @pytest.fixture(params=["node"])  # , "browser-main", "browser-worker"])
@pytest.fixture(params=["browser-main", "browser-worker"])
def backend_cli_settings(request):
    if request.param == "node":
        if ON_GITHUB_ACTIONS:
            return request.param, [
                "--node-binary",
                "/home/runner/micromamba-root/envs/dev-env/bin/node",
            ]
        else:
            return request.param, []
    else:
        return request.param, ["--headless"]


@pytest.fixture
def em_work_dir():
    return Path("/test")


@pytest.fixture
def runner():
    runner = CliRunner(mix_stderr=True)
    return runner
