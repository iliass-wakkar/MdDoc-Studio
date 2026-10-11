---
title: "MdDoc Enterprise Specification & Benchmark"
subtitle: "End-to-End Visual Verification for DOCX and PDF Backends"
author: "MdDoc Architecture Working Group"
date: "October 2026"
theme: "modern"
cover_page: true
toc: true
header: true
---

# Executive Summary

**MdDoc Studio** is a local-first, privacy-respecting document engineering platform designed to eliminate third-party cloud uploads while generating publication-quality executive artifacts.

> "True document design pairs semantic hierarchy with intentional typography."

---

# Design Heuristics & Visual Hierarchy

The platform automatically computes geometric page constraints, typographic scale, and color harmony across both Microsoft Word (`.docx`) and Typst (`.pdf`) outputs.

## Typographic Harmonization

Documents adhere to proportional typographic scales:

- **H1 (Primary Chapter / Section):** 20pt Bold with secondary color underline accent rule.
- **H2 (Major Topic):** 15pt Bold in secondary palette color.
- **H3 (Subtopic):** 12.5pt Bold in primary brand color.
- **Body Text:** 10.5pt with 1.15 line spacing and 4pt paragraph separation.

---

# Production Benchmark Matrix

The following table evaluates performance across the dual-compiler pipeline:

| Benchmark Criterion | Target Threshold | DOCX Engine (python-docx) | PDF Engine (Typst) | Status |
|---|:---:|:---:|:---:|---:|
| **Compilation Latency** | < 2.0s | ~0.45s | ~0.15s | Verified |
| **Zero Server Reliance** | 100% Client-Side | Yes (WASM / Python) | Yes (WASM / CLI) | Pass |
| **Booktabs Table Shading** | Alternate Zebra | Supported | Supported | Active |
| **Cover Page Generator** | Clean Geometric | Included | Included | Ready |

---

# System Callouts & Admonitions

> [!NOTE] Architecture Note
> The shared Intermediate Representation (IR) guarantees that callout variants map to matching border colors and background tints across formats.

> [!TIP] Pro Tip
> Use the Custom Theme Designer to bind your organization's exact corporate HEX colors and font families.

> [!IMPORTANT]
> All document conversions run entirely in client-side RAM with zero network uploads.

> [!WARNING] Production Safeguard
> Avoid storing unencrypted passwords or raw API keys in plain Markdown files.

> [!CAUTION] Critical Step
> Verify all table column headers before triggering production artifact distribution.

---

# Verification Code Block

```python
from mddoc.ir import markdown_to_ir
from mddoc.typst_compiler import compile_ir_to_typst

# Parse Markdown to Unified IR
doc_ir = markdown_to_ir(markdown_content)

# Emit Standalone Typst Code
typst_source = compile_ir_to_typst(doc_ir)
```

---

# Deployment Checklist

1. [x] Core parser compiles to shared AST.
2. [x] DOCX renderer applies booktabs borders and cover page.
3. [x] Typst compiler produces matching vector markup.
4. [ ] Production deployment synced with Cloudflare Pages.
