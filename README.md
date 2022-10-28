# pyjs-code-runner

Write cross platform build scripts with the power of Python!
To be used in the `boa` project.

Currently supports `CMake`, `Autotools`, `Meson` and `Make`.

## Examples

More coming soon!

### CMake

```bash
# run in node backend
pyjs_code_runner run script \
    node \
    --conda-env     /home/web_user/env \
    --mount         ~/src/pyjs/tests:/tests \
    --script        main.py \
    --work-dir      /tests \
    --async-main           

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
