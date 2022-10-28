# pyjs-code-runner

A driver to run python code in a wasm environment, almost like running vanilla python code.


## Examples




```bash
# run in node backend
pyjs_code_runner run script \
    node \
    --conda-env     /home/web_user/env           `# the emscripten-forge env in which to run the code` \
    --mount         ~/src/pyjs/tests:/tests      `# Mount path to virtual filesytem <HOST_MACHINE_PATH>:<TARGET_PATH>` \
    --script        main.py                      `# Path of the script to run (in virtual filesystem)` \
    --work-dir      /tests                       `# Work directory in the virtual fileystem` \
    --async-main                                 `# should a top-level async main function be called`

```


```bash
# run in browser-main-thread backend 
# in a headless fashion
pyjs_code_runner run script \
    browser-main \
    --conda-env     /home/web_user/env \
    --mount         ~/src/pyjs/tests:/tests \
    --script        main.py \
    --work-dir      /tests \
    --async-main           \
    --headless 

```


```bash
# run in browser-worker-thread backend 
# in a headless fashion
pyjs_code_runner run script \
    browser-worker                     \
    --conda-env     /home/web_user/env \
    --mount         ~/src/pyjs/tests:/tests \
    --script        main.py \
    --work-dir      /tests \
    --async-main           \
    --headless          

```


