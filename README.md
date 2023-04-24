# pyjs-code-runner

[![CI](https://github.com/emscripten-forge/pyjs-code-runner/actions/workflows/main.yaml/badge.svg)](https://github.com/emscripten-forge/pyjs-code-runner/actions/workflows/main.yaml)

A driver to run python code in a wasm environment, almost like running vanilla python code.

## Motivation

Debugging, experimenting and testing python code from a dedicated conda environment
in browser environment is a complex process with a lot of (complicated) steps.

* create the environment for emscripten
* pack the environemtn

## Installation

Currently `pyjs-code-runner` is not available on PyPI. To install it, clone the repository and install it with `pip`:

We first recommend to create a new conda environment for `pyjs-code-runner`:

```bash
mamba create -n pyjs-code-runner -c conda-forge python
mamba activate pyjs-code-runner
```

Then install `pyjs-code-runner`:

```bash
git clone https://github.com/emscripten-forge/pyjs-code-runner
cd pyjs-code-runner
python -m pip install -e .
```

Then install the browser for use with Playwright:

```bash
playwright install
```

You will then need another conda environment for the code you want to run in the browser. Here we specify the `emscripten-forge` channel and the `emscripten-32` platform:

```bash
mamba create -n my_env -c https://repo.mamba.pm/emscripten-forge -c https://repo.mamba.pm/conda-forge --platform=emscripten-32 python numpy pyjs
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