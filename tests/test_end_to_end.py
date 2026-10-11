"""
End-to-end integration test running the benchmark document through:
1. Markdown -> MdDoc IR -> DOCX -> Markdown (Roundtrip)
2. Markdown -> MdDoc IR -> Typst Output
"""

import os
import unittest
from mddoc.native_converter import convert_markdown_to_docx
from mddoc.docx_to_md import convert_docx_to_markdown
from mddoc.typst_compiler import compile_markdown_to_typst


class TestEndToEndPipeline(unittest.TestCase):
    def setUp(self):
        self.fixture_path = "fixtures/benchmark_document.md"
        with open(self.fixture_path, "r", encoding="utf-8") as f:
            self.benchmark_md = f.read()
        self.out_docx = "tests/test_benchmark_out.docx"

    def tearDown(self):
        if os.path.exists(self.out_docx):
            try:
                os.remove(self.out_docx)
            except Exception:
                pass

    def test_full_pipeline(self):
        # 1. Compile to DOCX
        convert_markdown_to_docx(
            md_content=self.benchmark_md,
            output_path=self.out_docx,
            theme_name="modern",
            show_cover=True,
            show_toc=True,
            show_header=True
        )
        self.assertTrue(os.path.exists(self.out_docx))
        self.assertGreater(os.path.getsize(self.out_docx), 1000)

        # 2. Roundtrip DOCX back to Markdown
        extracted_md = convert_docx_to_markdown(self.out_docx)
        self.assertIn("MdDoc Enterprise Specification & Benchmark", extracted_md)
        self.assertIn("Typographic Harmonization", extracted_md)
        self.assertIn("Production Benchmark Matrix", extracted_md)
        self.assertIn("Compilation Latency", extracted_md)

        # 3. Compile to Typst Source
        typst_code = compile_markdown_to_typst(self.benchmark_md)
        self.assertIn('#set page(', typst_code)
        self.assertIn('MdDoc Enterprise Specification & Benchmark', typst_code)
        self.assertIn('#admonition(variant: "NOTE"', typst_code)
        self.assertIn('#admonition(variant: "WARNING"', typst_code)
        self.assertIn('#table(', typst_code)


if __name__ == "__main__":
    unittest.main()
