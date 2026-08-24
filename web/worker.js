importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js");
importScripts("./mddoc_bundle.js?v=1.1.0");

let pyodide = null;
let isReady = false;

async function initPyodide() {
    try {
        postMessage({ type: "STATUS", message: "Loading WebAssembly Python Runtime..." });
        pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/"
        });

        postMessage({ type: "STATUS", message: "Installing python-docx & dependencies..." });
        await pyodide.loadPackage(["micropip"]);
        const micropip = pyodide.pyimport("micropip");

        // Install pure-python wheels
        await micropip.install([
            "python-docx",
            "markdown",
            "beautifulsoup4",
            "pyyaml"
        ]);

        postMessage({ type: "STATUS", message: "Mounting MdDoc engine..." });
        // Write bundled mddoc python package files into virtual filesystem
        pyodide.FS.mkdirTree("/home/pyodide/mddoc");
        for (const [filePath, content] of Object.entries(self.MDDOC_PYTHON_FILES || {})) {
            const fullPath = "/home/pyodide/" + filePath;
            pyodide.FS.writeFile(fullPath, content, { encoding: "utf8" });
        }

        // Initialize python conversion helper
        await pyodide.runPythonAsync(`
import sys
import io
sys.path.insert(0, '/home/pyodide')

from mddoc.native_converter import MarkdownToDocxConverter

def convert_md_to_docx_bytes(md_text, theme_name="modern", custom_theme=None, title=None, subtitle=None, author=None, date=None, show_cover=True, show_toc=True, page_size="A4"):
    converter = MarkdownToDocxConverter(
        theme_name=theme_name,
        custom_theme=custom_theme,
        title=title,
        subtitle=subtitle,
        author=author,
        date=date,
        show_cover=show_cover,
        show_toc=show_toc,
        page_size=page_size
    )
    doc = converter.convert(md_text)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()
`);

        isReady = true;
        postMessage({ type: "READY", message: "MdDoc Engine Ready" });
    } catch (err) {
        console.error("Pyodide Init Error:", err);
        postMessage({ type: "ERROR", message: "Failed to initialize WebAssembly engine: " + err.message });
    }
}

// Start Pyodide on worker load
initPyodide();

self.onmessage = async function (e) {
    const { action, id, payload } = e.data;

    if (action === "CONVERT") {
        if (!isReady) {
            postMessage({ id, type: "ERROR", message: "Engine is still initializing, please wait a moment..." });
            return;
        }

        try {
            const {
                markdown,
                theme = "modern",
                custom_theme = null,
                title = null,
                subtitle = null,
                author = null,
                date = null,
                show_cover = true,
                show_toc = true,
                page_size = "A4"
            } = payload;

            // Pass variables into Python global scope safely
            pyodide.globals.set("_md_input", markdown);
            pyodide.globals.set("_theme_input", theme);
            pyodide.globals.set("_custom_theme_input", custom_theme ? pyodide.toPy(custom_theme) : null);
            pyodide.globals.set("_title_input", title);
            pyodide.globals.set("_sub_input", subtitle);
            pyodide.globals.set("_author_input", author);
            pyodide.globals.set("_date_input", date);
            pyodide.globals.set("_cover_input", show_cover);
            pyodide.globals.set("_toc_input", show_toc);
            pyodide.globals.set("_size_input", page_size);

            const resultBytesProxy = await pyodide.runPythonAsync(`
convert_md_to_docx_bytes(
    _md_input,
    theme_name=_theme_input,
    custom_theme=_custom_theme_input,
    title=_title_input,
    subtitle=_sub_input,
    author=_author_input,
    date=_date_input,
    show_cover=_cover_input,
    show_toc=_toc_input,
    page_size=_size_input
)
`);

            const uint8Array = resultBytesProxy.toJs();
            resultBytesProxy.destroy();

            // Transfer ArrayBuffer for zero-copy high performance
            postMessage(
                { id, type: "CONVERT_SUCCESS", data: uint8Array },
                [uint8Array.buffer]
            );
        } catch (err) {
            console.error("Conversion Error:", err);
            postMessage({ id, type: "ERROR", message: err.message || "Conversion failed" });
        }
    }
};
