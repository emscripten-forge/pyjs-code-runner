
function cb(recived,total,n_finished, n_urls){
    console.log(`progress: ${recived}/${total} (${n_finished}/${n_urls})`)
}

async function fetchPackages(pyjs){
    let res = await fetch("./packages.json")
    if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
    }
    let packages = await res.json()
    let urls = packages.map(item => `./${item.filename}`)

    let arraybuffers = await pyjs._parallel_fetch_arraybuffers_with_progress_bar(urls,cb)


    let shared_libs = []
    // write all tarballs to the virtual filesystem
    pyjs.FS.mkdir("/package_tarballs")
    for(let i=0;i<urls.length;i++){
        console.log("writing",packages[i].filename)
        const tarball_path = `/package_tarballs/${packages[i].filename}`;
        pyjs.FS.writeFile(tarball_path, arraybuffers[i]);

        console.log("untar", packages[i].filename)
        let pkg_shared_libs = pyjs._untar(tarball_path, "/");
        shared_libs.push(pkg_shared_libs);
        console.log("shared_libs",pkg_shared_libs)
    }

    console.log("untar done, instantiating packages")
    // instantiate all packages
    for(let i=0;i<urls.length;i++){

        // replace .tar.gz with .json
        
        const json_fname = `${packages[i].filename_stem}.json`

        console.log("instantiating",packages[i].name)
        json_file = pyjs.FS.readFile(`/conda-meta/${json_fname}`)
        
        // parse json from arraybuffer
        let json = JSON.parse(new TextDecoder("utf-8").decode(json_file))

        // // if the shared lib path is not starting with "/"  then we prepand "/"
        // let pkg_shared_libs = shared_libs[i].map(lib => {
        //     if(lib.startsWith("/")){
        //         return lib
        //     }else{
        //         return `/${lib}`
        //     }
        // })
        
        // if the key "shared_library" is present, then we need to load the shared libraries
   
        await pyjs._loadDynlibsFromPackage(
            packages[i].name,
            false,
            shared_libs[i]
        )

        
    }
    console.log("instantiating packages done")

}


async function fetchMounts(pyjs){
    let response = await fetch("./mounts.json");
    if (!response.ok) {
        throw new Error(`HTTP error while fetching ./mounts.json! status: ${response.status}`);
    }
    let mounts = await response.json()
    pyjs.FS.mkdir("/mount_tarballs")
    
    for(let i=0;i<mounts.length;i++){
        let mount_fname = mounts[i];
        mount_url = `./${mount_fname}`;
        console.log("fetching",mount_url)
        let response = await fetch(mount_url);
        if (!response.ok) {
            throw new Error(`HTTP error while fetching ${mount_url}! status: ${response.status}`);
        }
        let mount = await response.arrayBuffer();
        let mount_array = new Uint8Array(mount);
        console.log("fetched size",mount_array.length)
        const mount_tarball_path = `/mount_tarballs/${mount_fname}`;

        console.log("writing",mount_tarball_path)
        pyjs.FS.writeFile(mount_tarball_path, mount_array);

        console.log("untar", mount_tarball_path)
        pyjs._untar(mount_tarball_path, "/");
    }
}



async function make_pyjs(print, error) {
    var pyjs = await createModule({print:print,error:print})
    var EmscriptenForgeModule = pyjs
    globalThis.EmscriptenForgeModule = pyjs
    globalThis.pyjs = pyjs

    // // download list of packages
    await fetchMounts(pyjs);
    await fetchPackages(pyjs);


    // const { default: importPackages }  = await import("./packed_env.js")
    // await importPackages();

    // const { default: importMounts }  = await import("./packed_mounts.js")
    // await importMounts();
        
    await pyjs.init()

    return pyjs
}

globalThis.make_pyjs = make_pyjs



function eval_main_script(pyjs, workdir, filename) {
    try{
        pyjs.exec("import os;from os.path import exists")
        pyjs.exec(`os.chdir("${workdir}")`)
        pyjs.eval_file(filename);
        return 0;
    }
    catch(e){
        console.error("error while evaluating main file:",e)
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

    while(true)
    {
        await new Promise(resolve => setTimeout(resolve, 100));
        const _async_done_ = pyjs.eval("_async_done_[0]")
        if(_async_done_)
        {
            break;
        }
    }
    return pyjs.eval("_ret_code[0]")
                
}
globalThis.run_async_python_main = run_async_python_main

// export { make_pyjs, run_async_python_main, eval_main_script };


if (typeof exports === 'object' && typeof module === 'object'){
    console.log("A")
  module.exports = make_pyjs;
}
else if (typeof define === 'function' && define['amd']){
    console.log("B")
  define([], function() { return make_pyjs; });
}
else if (typeof exports === 'object'){
    console.log("C")
  exports["make_pyjs"] = make_pyjs;
}
// else{
//     console.log("D")
//     export { make_pyjs, run_async_python_main, eval_main_script };
// }