# MdDoc Studio 📄✨

<div align="center">

[![Latest Release](https://img.shields.io/github/v/release/iliass-wakkar/MdDoc-Studio?color=blue&label=Latest%20Release&logo=github&style=for-the-badge)](https://github.com/iliass-wakkar/MdDoc-Studio/releases)
[![Download Windows App](https://img.shields.io/badge/Download-Windows%20EXE-2E8B8B?style=for-the-badge&logo=windows)](https://github.com/iliass-wakkar/MdDoc-Studio/releases/latest)
[![GitHub Stars](https://img.shields.io/github/stars/iliass-wakkar/MdDoc-Studio?style=for-the-badge&logo=github)](https://github.com/iliass-wakkar/MdDoc-Studio)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://github.com/iliass-wakkar/MdDoc-Studio/blob/main/LICENSE)

> **Markdown to Publication-Quality Microsoft Word (`.docx`) Converter**  
> Standalone, 100% offline, inspired by the document design heuristics of Kimi Skills.  
> Available as a single-click **Windows Desktop App (.exe)** and a **24/7 Free WebAssembly Studio**.

</div>

---

## 📥 Downloads & Version History

You can download the standalone desktop application directly from the **[GitHub Releases Page](https://github.com/iliass-wakkar/MdDoc-Studio/releases)**:

| Platform / Edition | Status | Download Link | Description |
|---|---|---|---|
| 🪟 **Windows Desktop App** | `v1.1.0` (Latest) | [⬇️ **Download `MdDoc.exe`**](https://github.com/iliass-wakkar/MdDoc-Studio/releases/latest) | **Single-file executable**: Double-click to open. Zero installation, zero terminal, zero dependencies. |
| 📦 **All Version Releases** | All Versions | [📋 **View All Releases & Changelogs**](https://github.com/iliass-wakkar/MdDoc-Studio/releases) | Complete list of all historical releases, release notes, and version assets. |
| 🌐 **Public Web Studio** | Online (24/7) | [🚀 **Launch Web Studio**](https://github.com/iliass-wakkar/MdDoc-Studio) | 100% Client-Side WebAssembly (WASM) in-browser converter. |

---

## 🌟 Key Features

- **🎨 5 Curated Design Themes:** Modern Tech, Nordic Minimal, Academic Classic, Forest Moss, and Corporate Blue.
- **⚡ Dual Engine Architecture:**
  - **Native Engine:** 100% Pure Python (`python-docx`). Zero external binaries required.
  - **Pandoc Engine:** Combines Pandoc reference templates with automated Python post-processing (zebra tables, callouts, header protection).
- **📑 Executive Cover Pages:** Clean title, subtitle, author, date, and geometric accent rules.
- **📊 Professional Tables:** Booktabs-inspired formatting, header shading, zebra striping, custom cell padding, and page-split protection (`cantSplit` & `tblHeader`).
- **💡 GitHub-Style Admonitions:** Natively renders `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, and `> [!CAUTION]` with icons and accent bars.
- **💻 Syntax Code Containers:** Padded code blocks with monospace font and subtle background shading.
- **🔄 Word-Native Table of Contents:** Generates native Word TOC field codes with page number dots.
- **👁️ Live Watch Mode:** Automatically re-compiles your `.docx` file every time you save your Markdown file.
- **🖱️ Windows Drag & Drop:** Drop any `.md` file onto `mddoc.bat` for instant conversion.

---

## 🚀 How to Launch (All-In-One Desktop App)

### 🥇 1. Standalone Single-Click App (`MdDoc.exe`)
- **Just double-click [`MdDoc.exe`](file:///c:/Users/ilias/Documents/GitHub/MdDoc/MdDoc.exe)**.
- **100% Standalone Windows Executable**: Everything (Python, libraries, themes, and UI) is packed into **one single `.exe` file**.
- No terminal window, no scripts, no setup needed. Double-click to open the full Document Studio window!

---

### 🌐 2. Browser Web Studio & Cloudflare Pages (Public Web App)
- **Local:** Double-click [`MdDoc_Web.bat`](file:///c:/Users/ilias/Documents/GitHub/MdDoc/MdDoc_Web.bat) or [`MdDoc_Web.vbs`](file:///c:/Users/ilias/Documents/GitHub/MdDoc/MdDoc_Web.vbs).
- **Public Cloudflare Pages:** Connect this repository to [Cloudflare Pages](https://dash.cloudflare.com/) (Build dir: `web`) to deploy a **100% free, 24/7 public web service** powered by in-browser WebAssembly. See [DEPLOY_CLOUDFLARE.md](file:///c:/Users/ilias/Documents/GitHub/MdDoc/DEPLOY_CLOUDFLARE.md) for 2-minute setup!
- Features: Drag-and-drop `.md` upload zone, interactive theme color palette cards, live split markdown editor, and one-click DOCX download.

---

### 🖱️ 3. Instant Drag & Drop (`mddoc.bat`)
- Simply drag and drop any `.md` file onto [`mddoc.bat`](file:///c:/Users/ilias/Documents/GitHub/MdDoc/mddoc.bat). The `.docx` file will be generated right next to it!

---

## 💻 Command Line Interface (CLI)

```bash
# Launch Native Desktop GUI
python mddoc.py --gui

# Launch Browser Web Studio
python mddoc.py --web

# Standard CLI conversion
python mddoc.py report.md -o report.docx --theme modern
```

---

## 🎨 Design Themes

| Theme | Heading Font | Body Font | Accent Color | Vibe |
|---|---|---|---|---|
| **`modern`** | Cambria | Calibri | `#1E3A5F` / `#2E8B8B` | Contemporary technical reports, proposals |
| **`nordic`** | Segoe UI Semibold | Segoe UI | `#2E3440` / `#5E81AC` | Clean Scandinavian minimalism, product specs |
| **`academic`** | Georgia | Georgia | `#1A365D` / `#744210` | Formal research papers, whitepapers |
| **`forest`** | Cambria | Calibri | `#1C4532` / `#2F855A` | Natural earthy palette, case studies |
| **`corporate`** | Arial | Arial | `#0F2942` / `#1E6091` | Executive briefs, enterprise strategy |

List all themes via CLI:
```bash
python mddoc.py --list-themes
```

---

## 📝 Markdown Frontmatter Support

Add YAML frontmatter at the top of your `.md` file to configure document metadata:

```yaml
---
title: "Quarterly Performance Report"
subtitle: "Executive Summary & Financial Metrics"
author: "Engineering Strategy Team"
date: "August 2026"
theme: "modern"
toc: true
cover_page: true
page_size: "A4"
---

# Executive Summary

Your markdown content here...
```

---

## 💡 Rich Elements & Callouts

### GitHub-Style Admonitions
```markdown
> [!NOTE]
> Information highlighting essential context.

> [!TIP]
> Use the `--watch` flag during editing.

> [!WARNING]
> Remember to right-click the TOC in Word to refresh page numbers.
```

### Tables with Automatic Header & Zebra Striping
```markdown
| Quarter | Revenue | Growth | Margin |
|---|---|---|---|
| Q1 | $12.4M | +18% | 34% |
| Q2 | $14.1M | +22% | 36% |
```

---

## 🛠️ Pre-Generating Pandoc Reference Templates

If you wish to use Pandoc directly with our pre-styled reference templates:

```bash
python generate_templates.py
```
This creates `templates/reference-<theme>.docx` for each theme. You can then run:

```bash
pandoc report.md -o report.docx --reference-doc=templates/reference-modern.docx --toc
```

---

## 🐍 Python API Usage

```python
from mddoc import convert_markdown_to_docx

convert_markdown_to_docx(
    input_path="input.md",
    output_path="output.docx",
    theme_name="nordic",
    show_cover=True,
    show_toc=True,
    page_size="A4"
)
```

---

## 🧪 Testing

Run the automated unit test suite:
```bash
python -m unittest discover tests
```

---

## 📄 License
MIT License. Free to use and customize offline forever.
