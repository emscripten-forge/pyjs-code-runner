# pyjs-code-runner

A driver to run python code in a wasm environment, almost like running vanilla python code.


## Examples



Here we assume a file `main.py` located at `~/foo/bar/main.py`.

```bash
pyjs_code_runner run script \
    node \
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

```


```bash
# run in browser-main-thread backend 
# in a headless fashion
pyjs_code_runner run script \
    browser-main \
    --conda-env     ~/micromamba/envs/my_env \
    --mount         ~/foo/bar:/home/web_user/fubar \
    --script        main.py \
    --work-dir      /tests \
    --async-main           \
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


