# pyjs-code-runner

[![CI](https://github.com/emscripten-forge/pyjs-code-runner/actions/workflows/main.yaml/badge.svg)](https://github.com/emscripten-forge/pyjs-code-runner/actions/workflows/main.yaml)

A driver to run python code in a wasm environment, almost like running vanilla python code.

## How it works

The script runs in a browser (playwright, main thread or web worker), driven by
the JavaScript of the pyjs npm package. Where pyjs and python come from:

* **a conda env** (`--conda-env`): an emscripten-forge env with **pyjs >= 6**.
  Its runtime and the npm JavaScript (`lib_js/pyjs/npm`, shipped by the pyjs
  conda package) are used, and the env is packed with empack. So exactly what
  is installed there runs, e.g. a python, pyjs and a package that were just
  built locally. This is what `pytester` (emscripten-forge recipe tests) uses.
* **an npm package** (`--pyjs-npm @scope/pyjs@6.0.0`, or a local package
  directory / `.tgz`): its own runtime and environment; extra conda packages
  with `--package <spec>` (repeatable) are installed at runtime.

Directories are mounted with `--mount <host dir>:<path in the browser>`.
pyjs < 6 envs are not supported anymore (use pyjs-code-runner 3.x).

## Installation

`pyjs_code_runner` is on conda-forge:

```bash
mamba install -c conda-forge pyjs_code_runner
playwright install chromium
```

You will then need an emscripten-forge environment for the code you want to run in the browser:

```bash
micromamba create -n my_env --platform=emscripten-wasm32 \
    -c https://repo.prefix.dev/emscripten-forge/6x -c conda-forge \
    python numpy "pyjs-dev>=6"
```

## Development

With [pixi](https://pixi.sh):

```bash
# npm mode: pyjs from the published npm package (what the CI runs)
pixi run test                        # chromium
pixi run test "chromium firefox webkit"
# conda mode: an emscripten-forge env with pyjs-dev >= 6 (local); a local
# recipe build (e.g. a new pyjs) is searched first:
PYJS_CODE_RUNNER_TEST_CHANNEL=/path/to/recipes/output pixi run test-conda
```

You might want to add more dependencies to this environment, depending on the code you would like to run.

## Usage

Here we assume a file `main.py` located at `~/foo/bar/main.py` with the following content:

```py
import numpy as np

print("Hello from pyjs-code-runner")
print("numpy version:", np.__version__)
```

You can then run this code in the browser with the following command:

```bash
# run in browser-main-thread backend
pyjs_code_runner run script                                                                \
    browser-main                                                                           \
    --conda-env     ~/micromamba/envs/my_env         `# the emscripten-forge env`          \
                                                     `# in which to run the code`          \
                                                                                           \
    --mount         ~/foo/bar:/home/web_user/fubar   `# Mount path to virtual filesytem`   \
                                                     `# <HOST_MACHINE_PATH>:<TARGET_PATH>` \
                                                                                           \
    --script        main.py                          `# Path of the script to run`         \
                                                     `# (in virtual filesystem)`           \
                                                                                           \
    --work-dir      /home/web_user/fubar             `# Work directory `                   \
                                                     `#in the virtual fileystem`           \
                                                                                           \
    --async-main                                     `# should a top-level async`          \
                                                     `# function named main be called`     \
    --headless

```

The `--headless` flag will run the browser in headless mode. If you want to see the browser open on your machine, you can remove this flag.

When you run this command you swill be able to see the output of the code in the terminal that looks like the following:

```bash
Failed to load resource: the server responded with a status of 404 (File not found)
fetching python package from ./python-3.10.2-h_hash_26_cpython.tar.gz
fetching pkg numpy from ./numpy-1.24.2-py310h6d2fff6_0.tar.gz
fetching pkg pip from ./pip-23.1-pyhd8ed1ab_0.tar.gz
fetching pkg setuptools from ./setuptools-63.4.2-py310h8bed8af_0.tar.gz
fetching pkg wheel from ./wheel-0.40.0-pyhd8ed1ab_0.tar.gz
fetching pkg pyparsing from ./pyparsing-3.0.9-pyhd8ed1ab_0.tar.gz
fetching pkg pyjs from ./pyjs-1.0.0-hc96583f_0.tar.gz
fetching pkg emscripten-abi from ./emscripten-abi-3.1.27-hb0f4dca_5.tar.gz
extract /package_tarballs/setuptools-63.4.2-py310h8bed8af_0.tar.gz (304 bytes)
extract /package_tarballs/wheel-0.40.0-pyhd8ed1ab_0.tar.gz (51524 bytes)
extract /package_tarballs/pyparsing-3.0.9-pyhd8ed1ab_0.tar.gz (90256 bytes)
extract /package_tarballs/pyjs-1.0.0-hc96583f_0.tar.gz (283 bytes)
extract /package_tarballs/emscripten-abi-3.1.27-hb0f4dca_5.tar.gz (302 bytes)
extract /package_tarballs/pip-23.1-pyhd8ed1ab_0.tar.gz (1319563 bytes)
extract /package_tarballs/python-3.10.2-h_hash_26_cpython.tar.gz (2279530 bytes)
extract /package_tarballs/numpy-1.24.2-py310h6d2fff6_0.tar.gz (3594626 bytes)
Hello from pyjs-code-runner
numpy version: 1.24.2
```

There are other ways to run the code, for example in a worker thread:

```bash
# run in browser-worker-thread backend
# in a headless fashion
pyjs_code_runner run script \
    browser-worker \
    --conda-env     ~/micromamba/envs/my_env \
    --mount         ~/foo/bar:/home/web_user/fubar \
    --script        main.py \
    --work-dir      /tests \
    --async-main           \
    --headless
```