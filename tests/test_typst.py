"""
Unit tests for the Typst PDF compiler from MdDoc IR.
"""

import unittest
from mddoc.typst_compiler import compile_markdown_to_typst


class TestTypstCompiler(unittest.TestCase):
    def test_compile_typst_output_structure(self):
        md = """---
title: "Quarterly Review"
subtitle: "Engineering Performance"
author: "Alex Morgan"
theme: "nordic"
cover_page: true
toc: true
---

# Executive Summary

This is a **high-priority** document.

> [!NOTE] Release Window
> Deployment scheduled for Friday night.

| Metric | Target | Result |
|---|---|---|
| Uptime | 99.9% | 99.99% |
| Latency | < 50ms | 38ms |

- Item Alpha
- Item Beta
"""
        typst_code = compile_markdown_to_typst(md)

        # 1. Assert document setup
        self.assertIn('#set page(', typst_code)
        self.assertIn('Quarterly Review', typst_code)
        self.assertIn('Engineering Performance', typst_code)
        self.assertIn('Alex Morgan', typst_code)

        # 2. Assert Table of Contents
        self.assertIn('#outline(title: "Table of Contents"', typst_code)

        # 3. Assert Admonition function and call
        self.assertIn('#let admonition(', typst_code)
        self.assertIn('#admonition(variant: "NOTE", title: "Release Window")', typst_code)
        self.assertIn('Deployment scheduled for Friday night.', typst_code)

        # 4. Assert Table syntax
        self.assertIn('#table(', typst_code)
        self.assertIn('Uptime', typst_code)
        self.assertIn('99.99%', typst_code)

        # 5. Assert Headings & Lists
        self.assertIn('= Executive Summary', typst_code)
        self.assertIn('- Item Alpha', typst_code)
        self.assertIn('- Item Beta', typst_code)


if __name__ == "__main__":
    unittest.main()
