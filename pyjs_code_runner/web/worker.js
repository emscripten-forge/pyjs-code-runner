// The script run in a web worker (index.html?worker). Output and the result
// go to the page with postMessage; the page prints / reports them.
import { run } from "./run.js";

const print = (text) => postMessage({ print: String(text) });
const printErr = (text) => postMessage({ printErr: String(text) });

// errors outside the awaited run end it (see index.html)
const describe = (error) => String(error && error.stack ? error.stack : error);
addEventListener("error", (event) => postMessage({ error: `uncaught: ${describe(event.error ?? event.message)}` }));
addEventListener("unhandledrejection", (event) => postMessage({ error: `unhandled rejection: ${describe(event.reason)}` }));

run(print, printErr).then(
  (code) => postMessage({ code }),
  (error) => postMessage({ error: String(error && error.stack ? error.stack : error) })
);
