import pytest
import subprocess
from pathlib import Path


@pytest.fixture(scope="session")
def env_prefix(tmp_path_factory):
    env_root = tmp_path_factory.mktemp("env")
    env_prefix = Path(env_root) / "env"

    print("prefix", env_prefix)
    channels = (
        "-c https://repo.mamba.pm/emscripten-forge -c https://repo.mamba.pm/conda-forge"
    )
    cmd = [
        f"""$MAMBA_EXE create --yes --prefix {str(env_prefix)} {channels} --platform=emscripten-32   python numpy pyjs """
    ]
    ret = subprocess.run(cmd, shell=True)
    #  stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    returncode = ret.returncode
    assert returncode == 0

    return env_prefix


@pytest.fixture(params=["node", "browser-main", "browser-worker"])
def backend_cli_settings(request):
    if request.param == "node":
        return request.param, []
    else:

        return request.param, ["--headless"]


@pytest.fixture
def to_mount_dir(tmpdir):
    path = Path(tmpdir)
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def em_work_dir():
    return Path("/test")


@pytest.fixture
def cli_mount(to_mount_dir, em_work_dir):
    return f"{str(to_mount_dir)}:{str(em_work_dir)}"
