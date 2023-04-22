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

Here we assume a file `main.py` located at `~/foo/bar/main.py`.

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