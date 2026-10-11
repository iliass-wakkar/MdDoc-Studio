"""
MdDoc Shared Intermediate Representation (IR / AST).
Provides a unified document model for multi-target compilation (DOCX, Typst PDF, HTML).
Ensures semantic consistency, theme parity, and layout predictability across all formats.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import re
import yaml
from datetime import datetime

try:
    from .themes import THEMES, get_theme
except (ImportError, ValueError):
    from mddoc.themes import THEMES, get_theme


@dataclass
class DocumentMetadata:
    title: Optional[str] = None
    subtitle: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    show_cover: bool = False
    show_toc: bool = False
    show_header: bool = False
    page_size: str = "A4"


@dataclass
class ThemePalette:
    name: str = "modern"
    primary: str = "1E3A5F"
    secondary: str = "2E8B8B"
    accent: str = "D4A373"
    font_heading: str = "Cambria"
    font_body: str = "Calibri"
    font_code: str = "Consolas"
    text: str = "2B2D42"
    light_text: str = "6C757D"
    background: str = "FFFFFF"
    table_header_bg: str = "1E3A5F"
    table_header_text: str = "FFFFFF"
    table_row_alt: str = "F8F9FA"
    table_border: str = "DEE2E6"


@dataclass
class InlineRun:
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    link: Optional[str] = None


@dataclass
class HeadingBlock:
    level: int  # 1 to 6
    text: str
    runs: List[InlineRun] = field(default_factory=list)


@dataclass
class ParagraphBlock:
    runs: List[InlineRun] = field(default_factory=list)


@dataclass
class CodeBlock:
    code: str
    language: Optional[str] = None


@dataclass
class BlockquoteBlock:
    paragraphs: List[ParagraphBlock] = field(default_factory=list)


@dataclass
class AdmonitionBlock:
    variant: str  # "NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"
    title: str
    content: List[ParagraphBlock] = field(default_factory=list)


@dataclass
class TableCell:
    text: str
    runs: List[InlineRun] = field(default_factory=list)
    is_header: bool = False
    align: str = "left"  # "left", "center", "right"


@dataclass
class TableRow:
    cells: List[TableCell] = field(default_factory=list)
    is_header: bool = False


@dataclass
class TableBlock:
    rows: List[TableRow] = field(default_factory=list)
    has_header: bool = True


@dataclass
class ListItem:
    runs: List[InlineRun] = field(default_factory=list)
    level: int = 0
    is_ordered: bool = False
    number: Optional[int] = None


@dataclass
class ListBlock:
    items: List[ListItem] = field(default_factory=list)
    is_ordered: bool = False


@dataclass
class HorizontalRuleBlock:
    pass


@dataclass
class DocumentModel:
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    theme: ThemePalette = field(default_factory=ThemePalette)
    blocks: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_inline_markdown(text: str) -> List[InlineRun]:
    """Parse inline bold, italic, inline code, and links into runs."""
    runs: List[InlineRun] = []
    
    # Combined regex tokenizer for inline markdown elements
    # 1: Code `...`
    # 2: Bold **...**
    # 3: Italic *...* or _..._
    # 4: Link [text](url)
    pattern = re.compile(
        r'(`(?P<code>[^`]+)`)'
        r'|(\*\*(?P<bold>[^*]+)\*\*)'
        r'|(\*(?P<italic>[^*]+)\*)'
        r'|(\[(?P<link_text>[^\]]+)\]\((?P<link_url>[^)]+)\))'
    )

    last_idx = 0
    for match in pattern.finditer(text):
        start, end = match.span()
        if start > last_idx:
            plain = text[last_idx:start]
            if plain:
                runs.append(InlineRun(text=plain))

        if match.group("code") is not None:
            runs.append(InlineRun(text=match.group("code"), code=True))
        elif match.group("bold") is not None:
            runs.append(InlineRun(text=match.group("bold"), bold=True))
        elif match.group("italic") is not None:
            runs.append(InlineRun(text=match.group("italic"), italic=True))
        elif match.group("link_text") is not None:
            runs.append(InlineRun(
                text=match.group("link_text"),
                link=match.group("link_url")
            ))

        last_idx = end

    if last_idx < len(text):
        remaining = text[last_idx:]
        if remaining:
            runs.append(InlineRun(text=remaining))

    return runs or [InlineRun(text=text)]


def markdown_to_ir(
    md_text: str,
    theme_name: str = "modern",
    custom_theme: Optional[Dict[str, Any]] = None,
    override_metadata: Optional[Dict[str, Any]] = None
) -> DocumentModel:
    """
    Parse Markdown text into the unified MdDoc DocumentModel (IR).
    Extracts YAML frontmatter, headings, admonitions, tables, and typography.
    """
    # 1. Parse Frontmatter
    frontmatter = {}
    body = md_text

    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', md_text, re.DOTALL)
    if fm_match:
        try:
            frontmatter = yaml.safe_load(fm_match.group(1)) or {}
        except Exception:
            frontmatter = {}
        body = md_text[fm_match.end():]

    overrides = override_metadata or {}

    # Metadata extraction
    title = overrides.get("title") or frontmatter.get("title")
    subtitle = overrides.get("subtitle") or frontmatter.get("subtitle")
    author = overrides.get("author") or frontmatter.get("author")
    date = overrides.get("date") or frontmatter.get("date") or datetime.now().strftime("%B %d, %Y")
    show_cover = overrides.get("show_cover") if "show_cover" in overrides else frontmatter.get("cover_page", False)
    show_toc = overrides.get("show_toc") if "show_toc" in overrides else frontmatter.get("toc", False)
    show_header = overrides.get("show_header") if "show_header" in overrides else (frontmatter.get("header", False) or frontmatter.get("running_header", False))
    page_size = overrides.get("page_size") or frontmatter.get("page_size", "A4")

    # Fallback title if not provided
    if not title:
        h1_m = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
        if h1_m:
            title = h1_m.group(1).strip()

    metadata = DocumentMetadata(
        title=str(title) if title else None,
        subtitle=str(subtitle) if subtitle else None,
        author=str(author) if author else None,
        date=str(date) if date else None,
        show_cover=bool(show_cover),
        show_toc=bool(show_toc),
        show_header=bool(show_header),
        page_size=str(page_size)
    )

    # 2. Theme Resolution
    tname = overrides.get("theme_name") or frontmatter.get("theme") or theme_name
    if custom_theme and isinstance(custom_theme, dict):
        td = custom_theme
        tname = "custom"
    else:
        td = get_theme(tname)

    theme_palette = ThemePalette(
        name=tname,
        primary=td.get("primary", "1E3A5F"),
        secondary=td.get("secondary", "2E8B8B"),
        accent=td.get("accent", "D4A373"),
        font_heading=td.get("font_heading", "Cambria"),
        font_body=td.get("font_body", "Calibri"),
        font_code=td.get("font_code", "Consolas"),
        text=td.get("text", "2B2D42"),
        light_text=td.get("light_text", "6C757D"),
        background=td.get("background", "FFFFFF"),
        table_header_bg=td.get("table_header_bg", "1E3A5F"),
        table_header_text=td.get("table_header_text", "FFFFFF"),
        table_row_alt=td.get("table_row_alt", "F8F9FA"),
        table_border=td.get("table_border", "DEE2E6")
    )

    doc_model = DocumentModel(metadata=metadata, theme=theme_palette)

    # 3. Parse Document Body into Blocks
    lines = body.splitlines()
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Blank lines
        if not stripped:
            i += 1
            continue

        # Horizontal Rule
        if re.match(r'^(?:-{3,}|\*{3,}|_{3,})$', stripped):
            doc_model.blocks.append(HorizontalRuleBlock())
            i += 1
            continue

        # Headings (# H1 to ###### H6)
        h_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if h_match:
            level = len(h_match.group(1))
            text = h_match.group(2).strip()
            runs = parse_inline_markdown(text)
            doc_model.blocks.append(HeadingBlock(level=level, text=text, runs=runs))
            i += 1
            continue

        # Fenced Code Block (```lang ... ```)
        if stripped.startswith("```"):
            lang = stripped[3:].strip() or None
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < n and lines[i].strip().startswith("```"):
                i += 1
            doc_model.blocks.append(CodeBlock(code="\n".join(code_lines), language=lang))
            continue

        # GFM Admonition Block (> [!NOTE] / > [!TIP] / etc.)
        admon_match = re.match(r'^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\](?:\s+(.*))?$', stripped, re.IGNORECASE)
        if admon_match:
            variant = admon_match.group(1).upper()
            custom_title = admon_match.group(2)
            default_titles = {
                "NOTE": "Note", "TIP": "Tip", "IMPORTANT": "Important",
                "WARNING": "Warning", "CAUTION": "Caution"
            }
            admon_title = custom_title.strip() if custom_title and custom_title.strip() else default_titles[variant]
            
            # Collect blockquote content
            admon_lines = []
            i += 1
            while i < n and (lines[i].strip().startswith(">") or (lines[i].strip() and not lines[i].strip().startswith("#"))):
                c_line = lines[i].strip()
                if c_line.startswith(">"):
                    c_line = c_line[1:].strip()
                if c_line.startswith("[!"):  # Next admonition
                    break
                admon_lines.append(c_line)
                i += 1

            p_blocks = []
            curr_p = []
            for al in admon_lines:
                if not al:
                    if curr_p:
                        p_blocks.append(ParagraphBlock(runs=parse_inline_markdown(" ".join(curr_p))))
                        curr_p = []
                else:
                    curr_p.append(al)
            if curr_p:
                p_blocks.append(ParagraphBlock(runs=parse_inline_markdown(" ".join(curr_p))))

            doc_model.blocks.append(AdmonitionBlock(
                variant=variant,
                title=admon_title,
                content=p_blocks or [ParagraphBlock(runs=[InlineRun(text="")])]
            ))
            continue

        # Standard Blockquote (> ...)
        if stripped.startswith(">"):
            quote_lines = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            quote_text = " ".join(quote_lines)
            doc_model.blocks.append(BlockquoteBlock(paragraphs=[
                ParagraphBlock(runs=parse_inline_markdown(quote_text))
            ]))
            continue

        # Markdown Table (| col1 | col2 |)
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines = []
            while i < n and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i].strip())
                i += 1

            if len(table_lines) >= 2:
                # Row 0: headers
                header_cells = [c.strip() for c in table_lines[0].strip("|").split("|")]
                # Row 1: separator row (e.g. |---|---|)
                alignments = []
                for sc in [c.strip() for c in table_lines[1].strip("|").split("|")]:
                    if sc.startswith(":") and sc.endswith(":"):
                        alignments.append("center")
                    elif sc.endswith(":"):
                        alignments.append("right")
                    else:
                        alignments.append("left")

                table_rows = []
                # Header row
                h_row = TableRow(is_header=True)
                for ci, hc in enumerate(header_cells):
                    al = alignments[ci] if ci < len(alignments) else "left"
                    h_row.cells.append(TableCell(text=hc, runs=parse_inline_markdown(hc), is_header=True, align=al))
                table_rows.append(h_row)

                # Data rows
                for rline in table_lines[2:]:
                    raw_cells = [c.strip() for c in rline.strip("|").split("|")]
                    d_row = TableRow(is_header=False)
                    for ci, dc in enumerate(raw_cells):
                        al = alignments[ci] if ci < len(alignments) else "left"
                        d_row.cells.append(TableCell(text=dc, runs=parse_inline_markdown(dc), is_header=False, align=al))
                    table_rows.append(d_row)

                doc_model.blocks.append(TableBlock(rows=table_rows, has_header=True))
                continue

        # Lists (Unordered - or *, Ordered 1.)
        bullet_m = re.match(r'^([\t\s]*)([-*+]|\d+\.)\s+(.+)$', line)
        if bullet_m:
            list_items = []
            is_ordered = bool(re.match(r'^\d+\.', bullet_m.group(2)))
            while i < n:
                bm = re.match(r'^([\t\s]*)([-*+]|\d+\.)\s+(.+)$', lines[i])
                if not bm:
                    break
                indent = len(bm.group(1))
                level = indent // 2
                item_text = bm.group(3).strip()
                list_items.append(ListItem(
                    runs=parse_inline_markdown(item_text),
                    level=level,
                    is_ordered=is_ordered
                ))
                i += 1
            doc_model.blocks.append(ListBlock(items=list_items, is_ordered=is_ordered))
            continue

        # Regular Paragraph
        para_lines = [stripped]
        i += 1
        while i < n and lines[i].strip() and not lines[i].strip().startswith(("#", ">", "```", "|", "- ", "* ", "1. ")):
            para_lines.append(lines[i].strip())
            i += 1
        full_p_text = " ".join(para_lines)
        doc_model.blocks.append(ParagraphBlock(runs=parse_inline_markdown(full_p_text)))

    return doc_model
