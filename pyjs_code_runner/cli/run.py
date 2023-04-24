from pathlib import Path
from typing import List, Optional
import typer


from .app import app
from .err import exit_with_err

from .utils import require_option, make_names
from ..run import run
from ..backend.backend import BackendType
from ..get_cache_dir import get_cache_dir
from ..get_file_filter import get_file_filter
from ..constants import EMSCRIPTEN_HOME

run_app = typer.Typer()
app.add_typer(run_app, name="run")

script_app = typer.Typer()
run_app.add_typer(script_app, name="script")


def parse_mounts(mounts):
    wrong_patter_exception = lambda m: exit_with_err(
        f"wrong pattern, must be: <to_mount>:<mount_path> but is `{m}`"
    )
    parsed_mounts = []
    for mount in mounts:
        n_colon = mount.count(":")
        if n_colon != 1:
            wrong_patter_exception(mount)

        res = mount.split(":")
        if len(res) != 2 or res[0] == "" or res[1] == "":
            wrong_patter_exception(mount)
        in_path, out_path = [Path(r) for r in res]

        if not in_path.exists():
            exit_with_err(
                f"to_mount path `{in_path}` from mount `{mount}` does not exist"
            )

        parsed_mounts.append((in_path, out_path))
    return parsed_mounts


conda_env_option = require_option(
    *make_names("conda-env"),
    help="host location of the conda environment in which to run the code",
)
script_option = require_option(
    *make_names("script"), help="path of script inside the virtual fileystem to run"
)
relocate_prefix_option = typer.Option(
    "/",
    *make_names("relocate-prefix"),
    help="location of the conda environment in the virtual file",
)
async_main_option = typer.Option(
    False,
    help="""run async main""",
)
mounts_option = typer.Option(
    ...,
    *make_names("mount"),
    help="<to_mount_file_or_directory>:<mount_location>",
)
work_dir_option = typer.Option(
    EMSCRIPTEN_HOME,
    *make_names("work-dir"),
    help="work-directory",
)
pkg_file_filter_option = typer.Option(  # noqa: B008
    None,
    *make_names("file-filter"),
    help="path to a .yaml file with the empack file-filter config",
)
pyjs_dir_option = typer.Option(
    None,
    *make_names("pyjs-dir"),
    help="""pyjs-directory, if None, pyjs from the conda-env is used""",
)
host_work_dir_option = typer.Option(
    None,
    *make_names("host-work-dir"),
    help="""host-work-directory, if host-work-dir is not specified, a temporary dir is used""",
)
cache_dir_option = typer.Option(
    None,
    *make_names("env-cache-dir"),
    help="""cache-directory, if env-cache-dir is not specified, the an `appdir` is used""",
)

cache_option = typer.Option(
    True,
    help="""use cache""",
)

port_option = typer.Option(
    None,
    "--port",
    help="""port used for serving the webpage""",
)

headless_option = typer.Option(
    False,
    help="""run browser headless""",
)

slowmo_option = typer.Option(
    None,
    "--slow-mo",
    help="""run browser in slow-mo (only when not in headless mode)""",
)


@script_app.command()
def browser_main(
    conda_env: Path = conda_env_option,
    script: Path = script_option,
    async_main: bool = async_main_option,
    mounts: List[str] = mounts_option,
    relocate_prefix: Optional[str] = relocate_prefix_option,
    work_dir: Optional[Path] = work_dir_option,
    pkg_file_filter: Optional[List[Path]] = pkg_file_filter_option,
    pyjs_dir: Optional[Path] = pyjs_dir_option,
    host_work_dir: Optional[Path] = host_work_dir_option,
    cache_dir: Optional[Path] = cache_dir_option,
    cache: bool = cache_option,
    port: Optional[int] = port_option,
    headless: bool = headless_option,
    slow_mo: Optional[int] = slowmo_option,
):
    run_script(
        backend_type=BackendType.browser_main,
        conda_env=conda_env,
        relocate_prefix=relocate_prefix,
        script=script,
        async_main=async_main,
        mounts=mounts,
        work_dir=work_dir,
        pkg_file_filter=pkg_file_filter,
        pyjs_dir=pyjs_dir,
        cache_dir=cache_dir,
        use_cache=cache,
        host_work_dir=host_work_dir,
        backend_kwargs=dict(port=port, headless=headless, slow_mo=slow_mo),
    )


@script_app.command()
def browser_worker(
    conda_env: Path = conda_env_option,
    script: Path = script_option,
    async_main: bool = async_main_option,
    mounts: List[str] = mounts_option,
    relocate_prefix: Optional[str] = relocate_prefix_option,
    work_dir: Optional[Path] = work_dir_option,
    pkg_file_filter: List[Path] = pkg_file_filter_option,
    pyjs_dir: Optional[Path] = pyjs_dir_option,
    host_work_dir: Optional[Path] = host_work_dir_option,
    cache_dir: Optional[Path] = cache_dir_option,
    cache: bool = cache_option,
    port: Optional[int] = port_option,
    headless: bool = headless_option,
    slow_mo: Optional[int] = slowmo_option,
):
    run_script(
        backend_type=BackendType.browser_worker,
        conda_env=conda_env,
        relocate_prefix=relocate_prefix,
        script=script,
        async_main=async_main,
        mounts=mounts,
        work_dir=work_dir,
        pkg_file_filter=pkg_file_filter,
        pyjs_dir=pyjs_dir,
        cache_dir=cache_dir,
        use_cache=cache,
        host_work_dir=host_work_dir,
        backend_kwargs=dict(port=port, headless=headless, slow_mo=slow_mo),
    )


node_binary_option = typer.Option(
    None,
    "--node-binary",
    help="""node exectutable""",
)


@script_app.command()
def node(
    conda_env: Path = conda_env_option,
    script: Path = script_option,
    async_main: bool = async_main_option,
    mounts: List[str] = mounts_option,
    relocate_prefix: Optional[str] = relocate_prefix_option,
    work_dir: Optional[Path] = work_dir_option,
    pkg_file_filter: List[Path] = pkg_file_filter_option,
    pyjs_dir: Optional[Path] = pyjs_dir_option,
    host_work_dir: Optional[Path] = host_work_dir_option,
    cache_dir: Optional[Path] = cache_dir_option,
    cache: bool = cache_option,
    node_binary: Optional[Path] = node_binary_option,
):
    run_script(
        backend_type=BackendType.node,
        conda_env=conda_env,
        relocate_prefix=relocate_prefix,
        script=script,
        async_main=async_main,
        mounts=mounts,
        work_dir=work_dir,
        pkg_file_filter=pkg_file_filter,
        pyjs_dir=pyjs_dir,
        cache_dir=cache_dir,
        use_cache=cache,
        host_work_dir=host_work_dir,
        backend_kwargs=dict(node_binary=node_binary),
    )


def run_script(
    backend_type,
    conda_env,
    relocate_prefix,
    script,
    async_main,
    mounts,
    work_dir,
    pkg_file_filter,
    pyjs_dir,
    host_work_dir,
    cache_dir,
    use_cache,
    backend_kwargs=None,
):
    if backend_kwargs is None:
        backend_kwargs = dict()
    mounts = parse_mounts(mounts)
    if use_cache:
        cache_dir = get_cache_dir(cache_dir=cache_dir)
    else:
        cache_dir = None
    pkg_file_filter = get_file_filter(pkg_file_filter)

    run(
        conda_env=conda_env,
        relocate_prefix=relocate_prefix,
        backend_type=backend_type,
        script=script,
        async_main=async_main,
        mounts=mounts,
        work_dir=work_dir,
        pkg_file_filter=pkg_file_filter,
        pyjs_dir=pyjs_dir,
        cache_dir=cache_dir,
        use_cache=use_cache,
        host_work_dir=host_work_dir,
        backend_kwargs=backend_kwargs,
    )
