"""
MdDoc - Markdown to Beautiful DOCX Toolkit
"""
__version__ = "1.0.0"

from .themes import THEMES, get_theme
from .native_converter import convert_markdown_to_docx

try:
    from .pandoc_converter import convert_with_pandoc, is_pandoc_available
    from .templates import generate_reference_docx, generate_all_reference_templates
except ImportError:
    # Running in browser / WebAssembly environment without subprocess
    convert_with_pandoc = None
    is_pandoc_available = lambda: False
    generate_reference_docx = None
    generate_all_reference_templates = None

__all__ = [
    "convert_markdown_to_docx",
    "convert_with_pandoc",
    "is_pandoc_available",
    "generate_reference_docx",
    "generate_all_reference_templates",
    "THEMES",
    "get_theme",
]
