
const fs = require('fs');
var path = require('path');

console.log(process.argv);
work_dir = process.argv[2];
script_path = process.argv[3];
async_main = parseInt(process.argv[4]);
host_work_dir =process.argv[5];

node_result_json = path.join(host_work_dir, '_node_result.json');


function report_error(e){
    let data = JSON.stringify({
        error: e,
        return_code: 1
    });
    fs.writeFileSync(node_result_json, data);
}

function report_no_run(){
    let data = JSON.stringify({
        error: "unknown error, code did not run properly",
        return_code: 1
    });
    fs.writeFileSync(node_result_json, data);
}

function report_success(e){
    let data = JSON.stringify({
        return_code: 0
    });
    fs.writeFileSync(node_result_json, data);
}
// a proper run will overwrite this
report_no_run();
(async () => {
    try {   
        const { default: createModule }  = await import("./pyjs_runtime_node.js")

    
        var pyjs = await createModule()
        var EmscriptenForgeModule = pyjs
        global.EmscriptenForgeModule = pyjs
        global.pyjs = pyjs


        const { default: importPackages }  = await import("./packed_env.js")
        await importPackages();

        const { default: importMounts }  = await import("./packed_mounts.js")
        await importMounts();

        await pyjs.init()

        try{
            pyjs.exec(`import os;os.chdir("${work_dir}")`)
            pyjs.eval_file(`${script_path}`);
        }
        catch(e){
            console.error("error while evaluating main file:",e)
            report_error(e);
            return;
        }
        if(async_main)
        {

            pyjs.exec(`\n
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
            let ret_code = pyjs.eval("_ret_code[0]");
            if(ret_code != 0)
            {   
                // process.exit(ret_code);
                report_error(Error("python_return_code!= 0"));
                return;
            }
        }
    } catch (e) {
       console.error(e)
       report_error(e);
       return;
    }
    report_success()
})();