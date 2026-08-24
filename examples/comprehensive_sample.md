---
title: "MdDoc Architecture & Feature Specification"
subtitle: "High-Performance Markdown to Publication-Quality Word DOCX"
author: "Engineering Team"
date: "August 2026"
theme: "modern"
toc: true
cover_page: true
---

# Executive Summary

**MdDoc** is an offline, standalone toolkit designed to convert standard Markdown files into beautifully formatted, publication-ready Microsoft Word documents (`.docx`). It combines the visual intelligence of modern design frameworks with the simplicity of offline tooling.

> "Simplicity is the ultimate sophistication. Good typography makes documents effortless to read and impactful to deliver."

---

# Design & Typography Architecture

Documents produced by **MdDoc** adhere to strict visual design principles, ensuring consistency across fonts, colors, and layout structure.

## Color Palette System

Each theme includes coordinated primary, secondary, and accent colors, accompanied by soft tint backgrounds for callouts and code blocks:

| Theme Name | Primary Color | Accent Hue | Typography Pairing | Recommended Use Case |
|---|---|---|---|---|
| **Modern Tech** | Deep Navy (`#1E3A5F`) | Warm Coral (`#E07A5F`) | Cambria + Calibri | Technical Reports & Proposals |
| **Nordic Minimal** | Charcoal (`#2E3440`) | Aurora Red (`#BF616A`) | Segoe UI Semibold + Segoe UI | Product Specs & Documentation |
| **Academic Classic** | Oxford Blue (`#1A365D`) | Russet Amber (`#C05621`) | Georgia + Georgia | Whitepapers & Research Papers |
| **Forest Moss** | Deep Green (`#1C4532`) | Ochre Gold (`#D69E2E`) | Cambria + Calibri | Environmental & Case Studies |
| **Corporate Blue** | Navy (`#0F2942`) | Cyan (`#00A896`) | Arial + Arial | Executive Briefs & Strategy |

## Callouts and Admonitions

MdDoc natively supports GitHub-style admonitions for notices, warnings, and tips:

> [!NOTE]
> This is an informational note highlighting key context or background details for the reader.

> [!TIP]
> Use the `--watch` flag in the CLI to automatically recompile your Word document whenever you save your Markdown file.

> [!IMPORTANT]
> Both conversion engines run 100% locally on your machine with zero external network calls.

> [!WARNING]
> When opening the generated document for the first time in Microsoft Word, right-click the Table of Contents and select **Update Field** to refresh page numbers.

> [!CAUTION]
> Avoid modifying Word OpenXML files directly without validating schema constraints.

---

# Code Snippets and Syntax

Code blocks are rendered in dedicated containers with soft background shading and clean borders:

```python
from mddoc import convert_markdown_to_docx

# Convert markdown directly to styled DOCX
output_path = convert_markdown_to_docx(
    input_path="report.md",
    output_path="report.docx",
    theme_name="modern",
    show_cover=True,
    show_toc=True
)
print(f"Document successfully created: {output_path}")
```

Inline code elements like `npm run build` or `python mddoc.py` are styled with monospace fonts and accent coloration.

---

# Feature Verification & Checklist

The following roadmap items are tracked and verified:

- [x] Dual-engine architecture (Native Python + Pandoc integration)
- [x] Five cohesive color themes (Modern, Nordic, Academic, Forest, Corporate)
- [x] Automated Cover Page generator with decorative accent geometry
- [x] Native Word Table of Contents field code
- [x] Styled Booktabs tables with zebra striping and cell padding
- [x] GitHub Flavored Markdown Admonitions (`[!NOTE]`, `[!WARNING]`, `[!TIP]`)
- [x] Windows drag-and-drop launcher (`mddoc.bat`)
- [x] Live `--watch` file compilation mode
- [x] Automated test suite covering all engines and themes
