// Runs the user's script with pyjs, in the main thread (index.html) or in a
// worker (worker.js). Everything comes from the directory this file is
// served from, prepared by pyjs_code_runner/run.py. `config.json` says what
// to run and where things are:
//
//   arch, work_dir, script, async_main, preload_shared_libs
//   pyjs        the directory of the pyjs npm package (its dist/*.js)
//   assets      the `assetsUrl`: <arch>/ with the runtime
//               (pyjs_runtime_browser.{mjs,wasm}) and a packed environment
//   packages    conda packages to install at runtime (npm mode)
//   archives    the mounts: tarballs unpacked into the file system
//
// The two sources (see run.py): a conda env (its runtime, its npm JS from
// lib_js/pyjs/npm, the env packed by empack: what pytester uses), or an npm
// package (its own JS, runtime and environment, + `packages`).
//
// Returns the exit code of the script: 0 if it ran through (and, with
// async_main, its `main()` returned None or 0), else non-zero.

// The python side: run the script as `python <script>` would (as __main__,
// its directory first on sys.path, in work_dir), then await `main()` if
// requested. Exceptions are printed, SystemExit gives the exit code.
const PYTHON_RUNNER = `
import os, runpy, sys, traceback

async def _pyjs_code_runner(work_dir, script, async_main):
    try:
        os.chdir(work_dir)
        sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
        sys.argv = [script]
        namespace = runpy.run_path(script, run_name="__main__")
        if async_main:
            result = await namespace["main"]()
            return 0 if result is None else int(result)
        return 0
    except SystemExit as e:
        if e.code is None:
            return 0
        if isinstance(e.code, int):
            return e.code
        print(e.code, file=sys.stderr)
        return 1
    except BaseException:
        traceback.print_exc()
        return 1
`;

export async function run(print, printErr) {
  const here = new URL(".", import.meta.url);
  const config = await (await fetch(new URL("config.json", here))).json();
  const entry = config.arch === "wasm64" ? "dist/wasm64.js" : "dist/index.js";
  const { default: initializePyjsRuntime } = await import(new URL(`${config.pyjs}/${entry}`, here).href);
  const pyjs = await initializePyjsRuntime({
    assetsUrl: new URL(`${config.assets}/`, here).href,
    // (never the CDN: everything must come from this directory)
    cdnFallback: false,
    packages: config.packages,
    archives: config.archives.map((a) => ({ url: new URL(a.url, here).href, path: a.path })),
    preloadSharedLibs: config.preload_shared_libs,
    // (every run is new: no package / bytecode cache in the browser profile)
    cache: false,
    print,
    printErr,
  });
  pyjs.runPython(PYTHON_RUNNER);
  const args = [config.work_dir, config.script, config.async_main].map((v) => JSON.stringify(v));
  // (JSON values are valid python literals here: strings and true / false)
  const code = await pyjs.runPythonAsync(
    `await _pyjs_code_runner(${args[0]}, ${args[1]}, ${config.async_main ? "True" : "False"})`
  );
  return Number(code);
}
