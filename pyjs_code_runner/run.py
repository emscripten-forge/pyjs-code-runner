"""Prepare a directory with everything a browser needs to run a python script
with pyjs, and run it there (backend/browser.py).

The page (web/) is driven by the JavaScript of the pyjs npm package. Where
pyjs and the python environment come from:

* a conda env (`conda_env`, the default; what pytester uses): an
  emscripten-forge env with pyjs >= 6 in it. Its runtime
  (lib_js/pyjs/pyjs_runtime_browser.{js,wasm}) and the npm package's
  JavaScript (lib_js/pyjs/npm) are used, and the whole env is packed with
  empack. So what runs is exactly what is installed there, e.g. a python,
  pyjs and some package that were just built locally.
* an npm package (`pyjs_npm`): a pyjs npm package (a version from the npm
  registry, or a local package directory / .tgz) with its own runtime and
  environment; `packages` are installed at runtime from the conda channels
  by the package's installer.

The directory served to the browser:

    index.html, worker.js, run.js   the page (web/)
    config.json                     what to run, read by run.js
    pyjs/                           the pyjs npm package (at least dist/)
    assets/<arch>/                  conda env mode: runtime + packed env
    mount_<i>.tar.gz                the mounts
"""

import json
import os
import shutil
import tarfile
import tempfile
import urllib.request
from contextlib import contextmanager
from pathlib import Path

from empack.file_patterns import pkg_file_filter_from_yaml
from empack.pack import DEFAULT_CONFIG_PATH as EMPACK_DEFAULT_CONFIG_PATH
from empack.pack import pack_directory, pack_env

from .backend.backend import BackendType, get_backend_cls
from .get_cache_dir import get_cache_dir

WEB_DIR = Path(__file__).resolve().parent / "web"
NPM_REGISTRY = "https://registry.npmjs.org"


def env_arch(conda_env):
    """"wasm32" or "wasm64": the platform of the packages in `conda_env`"""
    for meta in sorted((Path(conda_env) / "conda-meta").glob("*.json")):
        subdir = json.loads(meta.read_text()).get("subdir", "")
        if subdir.startswith("emscripten-"):
            return subdir.split("-", 1)[1]
    raise RuntimeError(f"{conda_env} has no emscripten-wasm32 / emscripten-wasm64 packages")


def install_runtime(source_dir, target_dir):
    """the runtime as the npm package wants it in assets/<arch>: the wasm
    and the emscripten glue as ES module (the conda package installs it as
    classic script: the module is the same text + an export)"""
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_dir / "pyjs_runtime_browser.wasm", target_dir / "pyjs_runtime_browser.wasm")
    glue = (source_dir / "pyjs_runtime_browser.js").read_text()
    (target_dir / "pyjs_runtime_browser.mjs").write_text(glue + "\nexport default createModule;\n")


def prepare_from_conda_env(conda_env, relocate_prefix, pyjs_dir, file_filter, use_cache, cache_dir, out):
    """conda env mode (see the module docstring); returns (arch, config)"""
    arch = env_arch(conda_env)
    # pyjs_dir: a directory like lib_js/pyjs of the env (runtime + npm/)
    pyjs_dir = Path(pyjs_dir) if pyjs_dir is not None else Path(conda_env) / "lib_js" / "pyjs"
    if not (pyjs_dir / "npm" / "dist" / "index.js").exists():
        raise RuntimeError(
            f"{pyjs_dir} has no npm/dist/index.js: pyjs-code-runner needs pyjs >= 6 in the env "
            "(its conda package ships the JavaScript of the npm package in lib_js/pyjs/npm)"
        )
    shutil.copytree(pyjs_dir / "npm", out / "pyjs")
    assets = out / "assets" / arch
    install_runtime(pyjs_dir, assets)
    pack_env(
        env_prefix=conda_env,
        relocate_prefix=relocate_prefix,
        file_filters=file_filter,
        use_cache=use_cache,
        cache_dir=cache_dir,
        outdir=assets,
        compresslevel=1,
    )
    return arch, dict(pyjs="pyjs", assets="assets", packages=[])


def split_npm_spec(spec):
    """"@scope/name@1.2.3" -> ("@scope/name", "1.2.3"); without a version:
    "latest". (A scoped name starts with an @ of its own.)"""
    scope = "@" if spec.startswith("@") else ""
    name, _, version = spec[len(scope):].partition("@")
    return scope + name, version or "latest"


def npm_package_dir(spec, cache_dir):
    """The directory of the npm package `spec`: a local package directory, a
    local .tgz, or "<name>@<version>" from the npm registry (downloaded once
    into the cache)."""
    path = Path(spec)
    if path.is_dir():
        return path
    if path.is_file():
        target = Path(cache_dir) / "npm" / path.name
        archive = path
    else:
        name, version = split_npm_spec(spec)
        with urllib.request.urlopen(f"{NPM_REGISTRY}/{name}/{version}") as response:
            meta = json.load(response)
        target = Path(cache_dir) / "npm" / f"{meta['name'].replace('/', '_')}-{meta['version']}"
        archive = target.with_suffix(".tgz")
        if not (target / "package").is_dir():
            target.parent.mkdir(parents=True, exist_ok=True)
            print(f"downloading {meta['name']}@{meta['version']}", flush=True)
            urllib.request.urlretrieve(meta["dist"]["tarball"], archive)
    if not (target / "package").is_dir():
        with tarfile.open(archive) as tar:
            tar.extractall(target, filter="data")
    return target / "package"


def prepare_from_npm(spec, arch, packages, cache_dir, out):
    """npm mode (see the module docstring); returns (arch, config)"""
    package = npm_package_dir(spec, cache_dir)
    shutil.copytree(package, out / "pyjs")
    if not (out / "pyjs" / "assets" / arch).is_dir():
        raise RuntimeError(f"the npm package {spec} has no runtime for {arch}")
    return arch, dict(pyjs="pyjs", assets="pyjs/assets", packages=list(packages or []))


def pack_mounts(mounts, out):
    """each (host directory, path in the virtual file system) as tarball;
    returns the `archives` entries of the npm package's initialize()"""
    archives = []
    for index, (host_path, em_path) in enumerate(mounts):
        host_path = Path(host_path)
        if not host_path.is_dir():
            raise RuntimeError(f"mount {host_path}: only directories can be mounted")
        name = f"mount_{index}.tar.gz"
        pack_directory(host_dir=host_path, mount_dir=str(em_path), outname=name, outdir=out, compresslevel=1)
        # (the entries are relative to "/": "home/web_user/...")
        archives.append(dict(url=name, path="/"))
    return archives


@contextmanager
def host_work_dir_context(host_work_dir=None):
    if host_work_dir is None:
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    else:
        host_work_dir = Path(host_work_dir)
        # (filled from scratch: copytree needs the targets to not exist)
        for entry in ["pyjs", "assets"]:
            shutil.rmtree(host_work_dir / entry, ignore_errors=True)
        host_work_dir.mkdir(parents=True, exist_ok=True)
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
    pyjs_npm=None,
    packages=None,
    arch="wasm32",
):
    """Run the python file `script` (path in the virtual file system, relative
    to `work_dir`) with pyjs in a browser; raises if it fails.

    conda env mode: `conda_env` (an emscripten-forge env with pyjs >= 6).
    npm mode: `pyjs_npm` ("<name>@<version>", a package directory or .tgz),
    `packages` (conda specs installed at runtime) and `arch`; `conda_env`
    is not used then (None).
    `mounts`: (host directory, directory in the virtual file system) pairs.
    `async_main`: after running the script, await its `main()`.
    `backend_kwargs`: port, headless, slow_mo, browser, preload_shared_libs.
    """
    if pkg_file_filter is None:
        pkg_file_filter = pkg_file_filter_from_yaml(EMPACK_DEFAULT_CONFIG_PATH)
    if cache_dir is None:
        cache_dir = get_cache_dir(cache_dir=None)
    backend_kwargs = dict(backend_kwargs or {})

    with host_work_dir_context(host_work_dir) as out:
        if pyjs_npm is not None:
            arch, config = prepare_from_npm(pyjs_npm, arch, packages, cache_dir, out)
        else:
            arch, config = prepare_from_conda_env(
                conda_env, str(relocate_prefix), pyjs_dir, pkg_file_filter, use_cache, cache_dir, out
            )
        config.update(
            arch=arch,
            archives=pack_mounts(mounts, out),
            work_dir=str(work_dir),
            script=str(script),
            async_main=bool(async_main),
            # (default as before: preloaded, also in a worker)
            preload_shared_libs=bool(backend_kwargs.pop("preload_shared_libs", True)),
        )
        (out / "config.json").write_text(json.dumps(config, indent=2))
        for name in ["index.html", "worker.js", "run.js"]:
            shutil.copyfile(WEB_DIR / name, out / name)

        backend = get_backend_cls(backend_type=backend_type)(host_work_dir=out, **backend_kwargs)
        backend.run()
