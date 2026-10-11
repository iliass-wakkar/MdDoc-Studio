"""
Unit tests for the MdDoc Intermediate Representation (IR).
"""

import unittest
from mddoc.ir import (
    markdown_to_ir,
    HeadingBlock,
    ParagraphBlock,
    CodeBlock,
    AdmonitionBlock,
    TableBlock,
    ListBlock,
    HorizontalRuleBlock
)


class TestMdDocIR(unittest.TestCase):
    def test_frontmatter_and_metadata(self):
        md = """---
title: "Architecture Specification"
subtitle: "Version 2.0"
author: "Engineering Lead"
date: "October 2026"
theme: "nordic"
cover_page: true
toc: true
header: true
---

# Introduction

This is the main introduction paragraph.
"""
        doc = markdown_to_ir(md)
        self.assertEqual(doc.metadata.title, "Architecture Specification")
        self.assertEqual(doc.metadata.subtitle, "Version 2.0")
        self.assertEqual(doc.metadata.author, "Engineering Lead")
        self.assertEqual(doc.metadata.date, "October 2026")
        self.assertTrue(doc.metadata.show_cover)
        self.assertTrue(doc.metadata.show_toc)
        self.assertTrue(doc.metadata.show_header)
        self.assertEqual(doc.theme.name, "nordic")

    def test_admonitions_parsing(self):
        md = """
> [!NOTE] Developer Note
> Make sure to cache tokens.

> [!WARNING]
> High CPU usage alert.
"""
        doc = markdown_to_ir(md)
        admons = [b for b in doc.blocks if isinstance(b, AdmonitionBlock)]
        self.assertEqual(len(admons), 2)
        self.assertEqual(admons[0].variant, "NOTE")
        self.assertEqual(admons[0].title, "Developer Note")
        self.assertEqual(admons[1].variant, "WARNING")
        self.assertEqual(admons[1].title, "Warning")

    def test_table_parsing(self):
        md = """
| Service | Port | Status |
|:---|:---:|---:|
| Web | 8080 | OK |
| API | 3000 | OK |
"""
        doc = markdown_to_ir(md)
        tables = [b for b in doc.blocks if isinstance(b, TableBlock)]
        self.assertEqual(len(tables), 1)
        tbl = tables[0]
        self.assertEqual(len(tbl.rows), 3)
        self.assertTrue(tbl.rows[0].is_header)
        self.assertEqual(tbl.rows[0].cells[0].text, "Service")
        self.assertEqual(tbl.rows[0].cells[1].align, "center")
        self.assertEqual(tbl.rows[0].cells[2].align, "right")

    def test_inline_runs(self):
        md = "This has **bold**, *italic*, `code`, and [Link](https://google.com)."
        doc = markdown_to_ir(md)
        self.assertTrue(len(doc.blocks) > 0)
        p = doc.blocks[0]
        self.assertIsInstance(p, ParagraphBlock)
        has_bold = any(r.bold for r in p.runs)
        has_italic = any(r.italic for r in p.runs)
        has_code = any(r.code for r in p.runs)
        has_link = any(r.link for r in p.runs)
        self.assertTrue(has_bold)
        self.assertTrue(has_italic)
        self.assertTrue(has_code)
        self.assertTrue(has_link)


if __name__ == "__main__":
    unittest.main()
