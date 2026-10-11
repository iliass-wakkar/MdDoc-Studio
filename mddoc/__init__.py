"""
MdDoc - Markdown to Beautiful DOCX Toolkit
"""
__version__ = "1.2.0"

from .themes import THEMES, get_theme
from .native_converter import convert_markdown_to_docx
from .ir import markdown_to_ir, DocumentModel
from .docx_to_md import convert_docx_to_markdown
from .typst_compiler import compile_markdown_to_typst, compile_ir_to_typst

try:
    from .pdf_tools import pdf_to_images, images_to_pdf, merge_pdfs, split_pdf
    from .pandoc_converter import convert_with_pandoc, is_pandoc_available
    from .templates import generate_reference_docx, generate_all_reference_templates
except ImportError:
    pdf_to_images = None
    images_to_pdf = None
    merge_pdfs = None
    split_pdf = None
    convert_with_pandoc = None
    is_pandoc_available = lambda: False
    generate_reference_docx = None
    generate_all_reference_templates = None

__all__ = [
    "convert_markdown_to_docx",
    "convert_docx_to_markdown",
    "compile_markdown_to_typst",
    "compile_ir_to_typst",
    "markdown_to_ir",
    "DocumentModel",
    "pdf_to_images",
    "images_to_pdf",
    "merge_pdfs",
    "split_pdf",
    "THEMES",
    "get_theme",
]
