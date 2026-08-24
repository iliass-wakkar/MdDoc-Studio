"""
Script to bundle the mddoc Python package into a JavaScript data file for Pyodide WebAssembly.
"""

import os
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
mddoc_dir = os.path.join(base_dir, "mddoc")

files_to_bundle = ["__init__.py", "themes.py", "oxml.py", "native_converter.py"]
bundle = {}

for fname in files_to_bundle:
    fpath = os.path.join(mddoc_dir, fname)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            bundle[f"mddoc/{fname}"] = f.read()

web_dir = os.path.join(base_dir, "web")
os.makedirs(web_dir, exist_ok=True)

out_file = os.path.join(web_dir, "mddoc_bundle.js")
with open(out_file, "w", encoding="utf-8") as f:
    f.write("// Auto-generated mddoc Python package bundle for Pyodide\n")
    f.write("self.MDDOC_PYTHON_FILES = ")
    json.dump(bundle, f, indent=2)
    f.write(";\n")

print(f"Bundled {len(bundle)} Python files into {out_file}")
