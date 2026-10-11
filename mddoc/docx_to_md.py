"""
High-Fidelity DOCX to Markdown Converter for MdDoc Studio.
Uses semantic extraction (Mammoth + BeautifulSoup) to turn Microsoft Word .docx
into clean, structured GitHub-Flavored Markdown (GFM).
Preserves headings, lists, tables, bold/italics, links, blockquotes, and code.
"""

import io
import re
from typing import Union, BinaryIO, Optional
from bs4 import BeautifulSoup, NavigableString, Tag


def _cell_to_md(cell_elem: Tag) -> str:
    """Extract and format text inside a table cell."""
    text_parts = []
    for child in cell_elem.descendants:
        if isinstance(child, NavigableString):
            text_parts.append(str(child))
    # Replace newlines with spaces within table cell
    clean = " ".join("".join(text_parts).split())
    # Escape pipe characters inside table cells
    return clean.replace("|", "\\|")


def _table_to_md(table_elem: Tag) -> str:
    """Convert an HTML <table> into GitHub-Flavored Markdown table syntax."""
    rows = table_elem.find_all("tr")
    if not rows:
        return ""

    table_data = []
    for r in rows:
        cells = r.find_all(["th", "td"])
        row_cells = [_cell_to_md(c) for c in cells]
        if row_cells:
            table_data.append(row_cells)

    if not table_data:
        return ""

    # Normalize column count across all rows
    max_cols = max(len(r) for r in table_data)
    for r in table_data:
        while len(r) < max_cols:
            r.append("")

    md_lines = []
    # Header row
    header_row = table_data[0]
    md_lines.append("| " + " | ".join(header_row) + " |")

    # Separator row
    separators = ["---" for _ in range(max_cols)]
    md_lines.append("| " + " | ".join(separators) + " |")

    # Data rows
    for row in table_data[1:]:
        md_lines.append("| " + " | ".join(row) + " |")

    return "\n" + "\n".join(md_lines) + "\n"


def _element_to_markdown(elem: Tag) -> str:
    """Recursively convert semantic HTML tag into Markdown text."""
    tag = elem.name.lower() if elem.name else ""

    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(tag[1])
        hashes = "#" * level
        text = _process_inline_children(elem).strip()
        # Clean redundant bold inside headings: # **Heading** -> # Heading
        if text.startswith("**") and text.endswith("**") and len(text) > 4:
            text = text[2:-2].strip()
        return f"\n{hashes} {text}\n"

    elif tag == "p":
        text = _process_inline_children(elem).strip()
        if not text:
            return ""
        # Detect manual bullet symbols (e.g. • or **•  **) that were not mapped to HTML <ul>
        bullet_cleaned = re.sub(r'^(?:\*\*)?[•·–—]\s*(?:\*\*)?\s*', '', text)
        if bullet_cleaned != text:
            return f"- {bullet_cleaned}"
        return f"\n{text}\n"

    elif tag == "blockquote":
        inner = _process_inline_children(elem).strip()
        lines = inner.split("\n")
        quoted = "\n".join(f"> {l}" for l in lines if l)
        return f"\n{quoted}\n"

    elif tag == "table":
        return _table_to_md(elem)

    elif tag in ("ul", "ol"):
        items = []
        is_ordered = (tag == "ol")
        for idx, li in enumerate(elem.find_all("li", recursive=False), 1):
            prefix = f"{idx}. " if is_ordered else "- "
            li_text = _process_inline_children(li).strip()
            items.append(f"{prefix}{li_text}")
        return "\n" + "\n".join(items) + "\n"

    elif tag == "pre":
        code_elem = elem.find("code")
        code_text = code_elem.get_text() if code_elem else elem.get_text()
        return f"\n```\n{code_text.strip()}\n```\n"

    elif tag == "hr":
        return "\n---\n"

    else:
        return _process_inline_children(elem)


def _process_inline_children(elem: Tag) -> str:
    """Convert inline tags like strong, em, code, a to markdown inline syntax."""
    out = []
    for child in elem.children:
        if isinstance(child, NavigableString):
            out.append(str(child))
        elif isinstance(child, Tag):
            t = child.name.lower()
            inner = _process_inline_children(child)
            if t in ("strong", "b"):
                out.append(f"**{inner}**")
            elif t in ("em", "i"):
                out.append(f"*{inner}*")
            elif t == "code":
                out.append(f"`{inner}`")
            elif t == "a":
                href = child.get("href", "")
                out.append(f"[{inner}]({href})" if href else inner)
            elif t == "img":
                src = child.get("src", "")
                alt = child.get("alt", "")
                out.append(f"![{alt}]({src})" if src else alt)
            elif t == "br":
                out.append("\n")
            elif t in ("ul", "ol", "table", "blockquote", "p", "h1", "h2", "h3", "h4", "h5", "h6", "div", "section", "article", "main", "header", "footer"):
                out.append(_element_to_markdown(child))
            else:
                out.append(inner)
    return "".join(out)


def convert_html_to_markdown(html_text: str) -> str:
    """Convert an HTML fragment or document to clean semantic Markdown."""
    soup = BeautifulSoup(html_text or "", "html.parser")
    for unwanted in soup.find_all(["script", "style", "noscript", "iframe"]):
        unwanted.decompose()
    root = soup.body if soup.body else soup
    md_blocks = []
    for elem in root.children:
        if isinstance(elem, Tag):
            block_text = _element_to_markdown(elem).strip()
            if block_text:
                md_blocks.append(block_text)
    full_md = "\n\n".join(md_blocks)
    return re.sub(r"\n{3,}", "\n\n", full_md).strip()


def sanitize_html_fragment(html_text: str) -> str:
    """Remove executable HTML from generated, locally saved HTML documents."""
    soup = BeautifulSoup(html_text or "", "html.parser")
    for unwanted in soup.find_all(["script", "iframe", "object", "embed"]):
        unwanted.decompose()
    for tag in soup.find_all(True):
        for attr_name in list(tag.attrs):
            normalized_name = attr_name.lower()
            value = tag.attrs.get(attr_name)
            if normalized_name.startswith("on"):
                del tag.attrs[attr_name]
                continue
            if normalized_name in {"href", "src", "action", "formaction", "xlink:href"} and isinstance(value, str):
                compact_value = re.sub(r"[\x00-\x20]+", "", value).lower()
                if compact_value.startswith(("javascript:", "vbscript:", "data:text/html")):
                    del tag.attrs[attr_name]
    return str(soup)


DEFAULT_STYLE_MAP = """
p[style-name^='Heading 1'] => h1:fresh
p[style-name^='heading 1'] => h1:fresh
p[style-name^='Heading 2'] => h2:fresh
p[style-name^='heading 2'] => h2:fresh
p[style-name^='Heading 3'] => h3:fresh
p[style-name^='heading 3'] => h3:fresh
p[style-name^='Heading 4'] => h4:fresh
p[style-name^='heading 4'] => h4:fresh
p[style-name^='Heading 5'] => h5:fresh
p[style-name^='heading 5'] => h5:fresh
p[style-name^='Heading 6'] => h6:fresh
p[style-name^='heading 6'] => h6:fresh
p[style-name='Title'] => h1:fresh
p[style-name='Subtitle'] => h2:fresh
"""


def convert_docx_to_markdown(
    docx_source: Union[str, BinaryIO, bytes],
    style_map: Optional[str] = None
) -> str:
    """
    Convert a .docx file (path, file-like object, or bytes) into clean Markdown.
    
    Args:
        docx_source: Path to .docx file, open binary file, or raw bytes.
        style_map: Optional Mammoth custom style mapping rules.
        
    Returns:
        Formatted GitHub-Flavored Markdown string.
    """
    s_map = style_map or DEFAULT_STYLE_MAP

    # Keep the package importable in runtimes that don't need Python-based
    # DOCX conversion (the browser uses Mammoth.js for that workflow).
    try:
        import mammoth
    except ImportError as exc:
        raise RuntimeError(
            "DOCX-to-Markdown conversion requires the 'mammoth' package. "
            "Install the project dependencies to use this Python converter."
        ) from exc

    if isinstance(docx_source, str):
        with open(docx_source, "rb") as f:
            result = mammoth.convert_to_html(f, style_map=s_map)
    elif isinstance(docx_source, bytes):
        bio = io.BytesIO(docx_source)
        result = mammoth.convert_to_html(bio, style_map=s_map)
    else:
        result = mammoth.convert_to_html(docx_source, style_map=s_map)

    html = result.value
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    root = soup.body if soup.body else soup

    md_blocks = []
    for elem in root.children:
        if isinstance(elem, Tag):
            block_text = _element_to_markdown(elem).strip()
            if block_text:
                md_blocks.append(block_text)

    full_md = "\n\n".join(md_blocks)
    # Normalize excessive newlines
    clean_md = re.sub(r'\n{3,}', '\n\n', full_md).strip()
    return clean_md
