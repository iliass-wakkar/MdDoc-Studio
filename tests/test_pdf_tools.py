"""
Unit tests for permissive PDF utilities in mddoc/pdf_tools.py.
"""

import os
import shutil
import unittest
from PIL import Image
from mddoc.pdf_tools import images_to_pdf, pdf_to_images, merge_pdfs, split_pdf


class TestPdfTools(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = "tests/tmp_pdf_tests"
        os.makedirs(self.tmp_dir, exist_ok=True)

        # Create two sample test images
        self.img1_path = os.path.join(self.tmp_dir, "test1.png")
        self.img2_path = os.path.join(self.tmp_dir, "test2.png")
        Image.new("RGB", (200, 200), color=(30, 58, 95)).save(self.img1_path)
        Image.new("RGB", (200, 200), color=(46, 139, 139)).save(self.img2_path)

        self.pdf_out = os.path.join(self.tmp_dir, "output.pdf")

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_images_to_pdf_and_render_back(self):
        # 1. Images -> PDF
        pdf_path = images_to_pdf([self.img1_path, self.img2_path], self.pdf_out)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 500)

        # 2. PDF -> Images
        rendered_images = pdf_to_images(pdf_path, self.tmp_dir, dpi=100, prefix="render")
        self.assertEqual(len(rendered_images), 2)
        for img in rendered_images:
            self.assertTrue(os.path.exists(img))

    def test_merge_and_split(self):
        # Create single-page PDFs
        p1 = os.path.join(self.tmp_dir, "p1.pdf")
        p2 = os.path.join(self.tmp_dir, "p2.pdf")
        images_to_pdf([self.img1_path], p1)
        images_to_pdf([self.img2_path], p2)

        # Merge
        merged = os.path.join(self.tmp_dir, "merged.pdf")
        merge_pdfs([p1, p2], merged)
        self.assertTrue(os.path.exists(merged))

        # Split
        split_dir = os.path.join(self.tmp_dir, "split")
        splits = split_pdf(merged, split_dir)
        self.assertEqual(len(splits), 2)


if __name__ == "__main__":
    unittest.main()
