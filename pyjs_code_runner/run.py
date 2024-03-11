from .backend.backend import BackendType, get_backend_type_family, get_backend_cls
from .work_dir_context import work_dir_context
from .get_cache_dir import get_cache_dir

import tempfile
from pathlib import Path
from empack.pack import pack_env, pack_directory,add_tarfile_to_env_meta
from empack.pack import DEFAULT_CONFIG_PATH as EMPACK_DEFAULT_CONFIG_PATH
from empack.file_patterns import pkg_file_filter_from_yaml

from contextlib import contextmanager
import os
import shutil
import json


def pack_mounts(mounts, host_work_dir, backend_type):
    mount_js_files = []
    for mount_index, (host_path, em_path) in enumerate(mounts):
        mount_filename = f"mount_{mount_index}.tar.gz"
        mount_js_files.append(mount_filename)
        if host_path.is_dir():
            pack_directory(
                host_dir=host_path,
                mount_dir=em_path,
                outname=mount_filename,
                outdir=host_work_dir,
                compresslevel=1,
            )

        elif host_path.is_file():
            raise RuntimeError("packing files is not yet supported")
        else:
            raise RuntimeError(
                f"host_path (={host_path}) in mounts is neither dir nor file"
            )
    with open(Path(host_work_dir) / "mounts.json", "w") as f:
        json.dump(mount_js_files, f, indent=4)
    return mount_js_files


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
        shutil.copyfile(Path(source_dir) / file, Path(outdir) / file)


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
    relocate_prefix,
    backend_type,
    script,
    async_main,
    mounts,
    work_dir,
    pkg_file_filter=None,
    pyjs_dir=None,
    cache_dir=None,
    use_cache=False,
    host_work_dir=None,
    backend_kwargs=None,
):
    relocate_prefix = str(relocate_prefix)
    if host_work_dir is not None:
        host_work_dir = Path(host_work_dir)

    if pkg_file_filter is None:
        pkg_file_filter = pkg_file_filter_from_yaml(EMPACK_DEFAULT_CONFIG_PATH)

    if backend_kwargs is None:
        backend_kwargs = dict()

    if cache_dir is None:
        cache_dir = get_cache_dir(cache_dir=None)

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
            env_prefix=conda_env,
            relocate_prefix=relocate_prefix,
            file_filters=pkg_file_filter,
            use_cache=use_cache,
            cache_dir=cache_dir,
            outdir=host_work_dir,
            compresslevel=9,
        ) 
        env_meta_filename = Path(host_work_dir) / "empack_env_meta.json"



        #raise RuntimeError("stop here")
        # pack all the mounts
        mount_files = pack_mounts(
            mounts=mounts,
            backend_type=backend_type,
            host_work_dir=host_work_dir,
        )
        for mount_file in mount_files:
            print(f"mount_file: {mount_file}")
            try:
                add_tarfile_to_env_meta(
                    env_meta_filename=env_meta_filename, tarfile=mount_file
                )
            except shutil.SameFileError:
                pass

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
