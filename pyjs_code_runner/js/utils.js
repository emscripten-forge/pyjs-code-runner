async function fetchMount(pyjs, mount){
    let url = `./${mount}`;
    let filename = `/mount_tarballs/${mount}`;
    let byte_array = await pyjs._fetch_byte_array(url, filename);
    pyjs.FS.writeFile(filename, byte_array);
    pyjs._untar_from_python(filename, "/");
}

async function fetchMounts(pyjs) {
    let response = await fetch("./mounts.json");
    if (!response.ok) {
        throw new Error(`HTTP error while fetching ./mounts.json! status: ${response.status}`);
    }
    let mounts = await response.json();
    pyjs.FS.mkdir("/mount_tarballs");
    await Promise.all(mounts.map(mount => fetchMount(pyjs, mount)));
    
}

async function make_pyjs(print, error) {
    var pyjs = await createModule({ print: print, error: print })
    
   await pyjs.bootstrap_from_empack_packed_environment(
        `./empack_env_meta.json`, /* packages_json_url */
        ".",               /* package_tarballs_root_url */
        false              /* verbose */
    );
    globalThis.pyjs = pyjs
    return pyjs
}

globalThis.make_pyjs = make_pyjs

function eval_main_script(pyjs, workdir, filename) {
    try {
        pyjs.exec("import os;from os.path import exists")
        pyjs.exec(`os.chdir("${workdir}")`)
        pyjs.eval_file(filename);
        return 0;
    }
    catch (e) {
        console.error("error while evaluating main file:", e)
        return 1;
    }
    return 0
}
globalThis.eval_main_script = eval_main_script

async function run_async_python_main(pyjs) {


    pyjs.exec(`
import asyncio
_async_done_ = [False]
_ret_code = [0]
async def main_runner():
    try:
        ret = await main()
        if ret is None:
            ret = 0
        _ret_code[0] = ret
    except Exception as e:
        _ret_code[0] = 1
        print("EXCEPTION",e)
    finally:
        global _async_done_
        _async_done_[0] = True
asyncio.ensure_future(main_runner())
    `)

    while (true) {
        await new Promise(resolve => setTimeout(resolve, 100));
        const _async_done_ = pyjs.eval("_async_done_[0]")
        if (_async_done_) {
            break;
        }
    }
    return pyjs.eval("_ret_code[0]")

}
globalThis.run_async_python_main = run_async_python_main


if (typeof exports === 'object' && typeof module === 'object') {
    module.exports = make_pyjs;
}
else if (typeof define === 'function' && define['amd']) {
    define([], function () { return make_pyjs; });
}
else if (typeof exports === 'object') {
    exports["make_pyjs"] = make_pyjs;
}
