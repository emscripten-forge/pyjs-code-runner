from rich.pretty import pprint
from .backend.backend import BackendType, get_backend_type_family, get_backend_cls
from .constants import EXPORT_NAME_SUFFIX
from .js_global_object import js_global_object
from .work_dir_context import work_dir_context
import tempfile
from pathlib import Path
from empack.file_packager import pack_directory, pack_file, split_pack_environment
from contextlib import contextmanager
import os
import shutil


def pack_mounts(mounts, host_work_dir, backend_type, outdir):
    export_name = f"{js_global_object(backend_type)}.{EXPORT_NAME_SUFFIX}"

    mount_js_files = []
    for mount_index, (host_path, em_path) in enumerate(mounts):
        mount_name = f"mount_{mount_index}"
        mount_js_files.append(f"{mount_name}.js")
        if host_path.is_dir():
            with work_dir_context(outdir):
                pack_directory(
                    directory=host_path,
                    mount_path=em_path,
                    outname=mount_name,
                    export_name=export_name,
                    silent=True,
                )
        elif host_path.is_file():
            raise RuntimeError("packing files is not yet supported")
        else:
            raise RuntimeError(
                f"host_path (={host_path}) in mounts is neither dir nor file"
            )

    import_statements = [
        f'promises.push(import("./{mod_name}"));' for mod_name in mount_js_files
    ]

    push_promises = "\n".join(import_statements)
    if backend_type == BackendType.node:
        module_code = f"""
        async  function importMounts(){{
            let promises = [];
            {push_promises}
            await Promise.all(promises);
        }}\n
        module.exports = importMounts
        """
    else:
        module_code = f"""
        export default async  function(){{
            let promises = [];
            {push_promises}
            await Promise.all(promises);
        }}\n
        """

    with open(outdir / "packed_mounts.js", "w") as f:
        f.write(module_code)


def conda_env_to_cache_name(conda_env, backend_type):
    env_name = str(conda_env).replace(os.path.sep, "_")
    folder_name = (
        f"{env_name}__backend_family__{get_backend_type_family(backend_type).value}"
    )
    return folder_name


def copy_pyjs(conda_env, backend_type, pyjs_dir, outdir):
    if backend_type == BackendType.node:
        files = ["pyjs_runtime_node.js", "pyjs_runtime_node.wasm"]
    else:
        files = ["pyjs_runtime_browser.js", "pyjs_runtime_browser.wasm"]

    # if user specified pyjs dir we prefer this
    if pyjs_dir is not None:
        source_dir = Path(pyjs_dir)
    else:
        source_dir = Path(conda_env) / "lib_js/pyjs/"
        if not source_dir.exists():
            raise RuntimeError(
                f"{conda_env} does not contain pyjs. use pyjs-dir argument or install pyjs in env"
            )

    for file in files:
        shutil.copyfile(source_dir / file, outdir / file)


def pack_env(conda_env, backend_type, pkg_file_filter, cache_dir, outdir):

    outname = "packed_env"
    cache_folder_name = Path(
        conda_env_to_cache_name(conda_env, backend_type=backend_type)
    )
    folder_for_env = cache_dir / cache_folder_name
    file_to_probe = folder_for_env / f"{outname}.js"
    if not file_to_probe.exists():
        folder_for_env.mkdir(parents=True, exist_ok=True)

        export_name = f"{js_global_object(backend_type)}.{EXPORT_NAME_SUFFIX}"

        with work_dir_context(folder_for_env):
            split_pack_environment(
                env_prefix=conda_env,
                outname=outname,
                export_name=export_name,
                pkg_file_filter=pkg_file_filter,
            )

    # copy from cache to work dir
    shutil.copytree(folder_for_env, outdir, dirs_exist_ok=True)


@contextmanager
def host_work_dir_context(host_work_dir=None):
    if host_work_dir is None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with work_dir_context(temp_dir):
                yield Path(temp_dir)
    else:
        with work_dir_context(host_work_dir):
            yield host_work_dir


def run(
    conda_env,
    backend_type,
    script,
    async_main,
    mounts,
    work_dir,
    pkg_file_filter,
    pyjs_dir,
    cache_dir,
    host_work_dir,
    backend_kwargs,
):

    # create a temporary host work directory
    with host_work_dir_context(host_work_dir) as host_work_dir:

        # copy pyjs-runtime to host-work-dir
        copy_pyjs(
            conda_env=conda_env,
            backend_type=backend_type,
            pyjs_dir=pyjs_dir,
            outdir=host_work_dir,
        )
        # pack the environment itself
        pack_env(
            conda_env=conda_env,
            backend_type=backend_type,
            outdir=host_work_dir,
            pkg_file_filter=pkg_file_filter,
            cache_dir=cache_dir,
        )

        # pack all the mounts
        mount_js_files = pack_mounts(
            mounts=mounts,
            host_work_dir=host_work_dir,
            backend_type=backend_type,
            outdir=host_work_dir,
        )

        # get the backend where the wasm code runs (ie node/browser-main/browser-worker)
        backend = get_backend_cls(backend_type=backend_type)(
            host_work_dir=host_work_dir,
            work_dir=work_dir,
            script=script,
            async_main=async_main,
            **backend_kwargs,
        )

        # run
        backend.run()
