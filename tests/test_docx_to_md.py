"""
Unit tests for DOCX to Markdown conversion.
Tests round-trip fidelity between Markdown -> DOCX -> Markdown.
"""

import os
import unittest
from mddoc.native_converter import convert_markdown_to_docx
from mddoc.docx_to_md import convert_docx_to_markdown


class TestDocxToMarkdown(unittest.TestCase):
    def setUp(self):
        self.test_docx_path = "tests/test_sample_output.docx"

    def tearDown(self):
        if os.path.exists(self.test_docx_path):
            try:
                os.remove(self.test_docx_path)
            except Exception:
                pass

    def test_roundtrip_headings_and_styles(self):
        source_md = """# Project Scope

This is an important overview of the system architecture.

## Database Schema

We use PostgreSQL for all relational data.

- User accounts
- Access logs
- Billing records
"""
        # 1. Create DOCX from Markdown
        convert_markdown_to_docx(
            md_content=source_md,
            output_path=self.test_docx_path,
            show_cover=False,
            show_toc=False,
            show_header=False
        )

        # 2. Convert DOCX back to Markdown
        extracted_md = convert_docx_to_markdown(self.test_docx_path)

        # 3. Assert fidelity
        self.assertIn("# Project Scope", extracted_md)
        self.assertIn("## Database Schema", extracted_md)
        self.assertIn("User accounts", extracted_md)
        self.assertIn("Access logs", extracted_md)

    def test_roundtrip_tables(self):
        source_md = """# System Matrix

| Component | Port | Status |
|---|---|---|
| Gateway | 80 | Active |
| Auth | 443 | Secure |
"""
        convert_markdown_to_docx(
            md_content=source_md,
            output_path=self.test_docx_path,
            show_cover=False,
            show_toc=False,
            show_header=False
        )

        extracted_md = convert_docx_to_markdown(self.test_docx_path)
        self.assertIn("Component", extracted_md)
        self.assertIn("Gateway", extracted_md)
        self.assertIn("Auth", extracted_md)
        self.assertIn("|", extracted_md)


if __name__ == "__main__":
    unittest.main()
