"""
Lightweight, Permissive PDF Utilities for MdDoc Studio.
Uses pypdf (BSD-3-Clause) and pypdfium2 (BSD/Apache-2.0).
Zero AGPL licensing traps. 100% offline and safe for commercial/distribution use.
"""

import os
import tempfile
from typing import List, Optional, Tuple
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
import pypdfium2 as pdfium


def pdf_to_images(
    pdf_path: str,
    output_dir: str,
    dpi: int = 200,
    prefix: str = "page"
) -> List[str]:
    """
    Render PDF pages to high-resolution PNG images.
    
    Args:
        pdf_path: Absolute or relative path to source PDF.
        output_dir: Directory where PNG files will be saved.
        dpi: Resolution (default: 200 DPI).
        prefix: Filename prefix.
        
    Returns:
        List of generated image file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    pdf = pdfium.PdfDocument(pdf_path)
    output_files = []

    # Calculate scale factor relative to 72 points/inch standard PDF resolution
    scale = dpi / 72.0

    for i, page in enumerate(pdf):
        page_num = i + 1
        image = page.render(scale=scale).to_pil()
        out_file = os.path.join(output_dir, f"{prefix}_{page_num:03d}.png")
        image.save(out_file, "PNG")
        output_files.append(out_file)

    return output_files


def images_to_pdf(
    image_paths: List[str],
    output_pdf_path: str,
    page_format: str = "image"
) -> str:
    """
    Convert images into a PDF using either image-sized pages or A4 pages.
    
    Args:
        image_paths: List of paths to source images.
        output_pdf_path: Target path for the output PDF.
        page_format: "image" to size each page to its image, or "a4" to
            fit each image proportionally on an A4 page with a white background.
        
    Returns:
        Path to generated PDF file.
    """
    if not image_paths:
        raise ValueError("At least one image path must be provided.")
    if page_format not in {"image", "a4"}:
        raise ValueError("page_format must be either 'image' or 'a4'.")

    from PIL import Image, ImageOps

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)

    pil_images = []
    for p in image_paths:
        with Image.open(p) as source:
            oriented = ImageOps.exif_transpose(source).convert("RGBA")
            image = Image.new("RGB", oriented.size, (255, 255, 255))
            image.paste(oriented, mask=oriented.getchannel("A"))

        if page_format == "a4":
            # A4 at 100 DPI, matching the resolution used for the output PDF.
            a4_portrait = (827, 1169)
            page_size = a4_portrait if image.height >= image.width else tuple(reversed(a4_portrait))
            scale = min(page_size[0] / image.width, page_size[1] / image.height)
            resampling = getattr(Image, "Resampling", Image).LANCZOS
            fitted_size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
            fitted = image.resize(fitted_size, resampling)
            a4_page = Image.new("RGB", page_size, (255, 255, 255))
            offset = ((page_size[0] - fitted.width) // 2, (page_size[1] - fitted.height) // 2)
            a4_page.paste(fitted, offset)
            image = a4_page

        pil_images.append(image)

    first = pil_images[0]
    rest = pil_images[1:] if len(pil_images) > 1 else []
    if page_format == "image":
        first.save(output_pdf_path, "PDF", resolution=100.0, save_all=True, append_images=rest)
    else:
        # Pillow writes pixel-based page sizes. Set the PDF page boxes to the
        # exact A4 point dimensions after rasterizing the fitted page artwork.
        with tempfile.NamedTemporaryFile(suffix=".pdf", dir=os.path.dirname(os.path.abspath(output_pdf_path)), delete=False) as temp_file:
            temp_pdf_path = temp_file.name
        try:
            first.save(temp_pdf_path, "PDF", resolution=100.0, save_all=True, append_images=rest)
            reader = PdfReader(temp_pdf_path)
            writer = PdfWriter()
            a4_long, a4_short = 841.88976378, 595.27559055
            for page, image in zip(reader.pages, pil_images):
                page_width, page_height = (a4_short, a4_long) if image.height >= image.width else (a4_long, a4_short)
                exact_a4 = RectangleObject([0, 0, page_width, page_height])
                page.mediabox = exact_a4
                page.cropbox = exact_a4
                writer.add_page(page)
            with open(output_pdf_path, "wb") as output_file:
                writer.write(output_file)
        finally:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

    return os.path.abspath(output_pdf_path)


def merge_pdfs(
    pdf_paths: List[str],
    output_pdf_path: str
) -> str:
    """
    Merge multiple PDF documents into a single document.
    """
    if not pdf_paths:
        raise ValueError("At least one PDF file path must be provided.")

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
    writer = PdfWriter()

    for p in pdf_paths:
        reader = PdfReader(p)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    return os.path.abspath(output_pdf_path)


def split_pdf(
    pdf_path: str,
    output_dir: str,
    page_ranges: Optional[List[Tuple[int, int]]] = None
) -> List[str]:
    """
    Split a PDF into single pages or specified page ranges.
    
    Args:
        pdf_path: Source PDF path.
        output_dir: Directory where split PDFs will be written.
        page_ranges: Optional list of 1-indexed (start, end) tuples.
        
    Returns:
        List of generated PDF file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_files = []

    if page_ranges:
        for idx, (start, end) in enumerate(page_ranges, 1):
            s_idx = max(0, start - 1)
            e_idx = min(total_pages, end)
            writer = PdfWriter()
            for p_num in range(s_idx, e_idx):
                writer.add_page(reader.pages[p_num])
            out_file = os.path.join(output_dir, f"{base_name}_part_{idx}.pdf")
            with open(out_file, "wb") as f:
                writer.write(f)
            output_files.append(out_file)
    else:
        # Split every page into separate file
        for p_num in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[p_num])
            out_file = os.path.join(output_dir, f"{base_name}_page_{p_num + 1:03d}.pdf")
            with open(out_file, "wb") as f:
                writer.write(f)
            output_files.append(out_file)

    return output_files


def rotate_pdf(
    pdf_path: str,
    output_pdf_path: str,
    rotation: int = 90,
    pages: Optional[List[int]] = None
) -> str:
    """
    Rotate pages in a PDF document by a specified degree.
    
    Args:
        pdf_path: Path to the input PDF.
        output_pdf_path: Path to the output PDF.
        rotation: Degrees to rotate clockwise (e.g., 90, 180, 270).
        pages: Optional list of 1-indexed page numbers to rotate. If None, rotates all pages.
        
    Returns:
        Absolute path to rotated PDF.
    """
    if rotation % 90 != 0:
        raise ValueError("Rotation angle must be a multiple of 90 degrees.")

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        if pages is None or page_num in pages:
            page.rotate(rotation)
        writer.add_page(page)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    return os.path.abspath(output_pdf_path)


def extract_pdf_text(
    pdf_path: str,
    page_numbers: Optional[List[int]] = None
) -> str:
    """
    Extract readable text content from PDF pages.
    
    Args:
        pdf_path: Path to source PDF.
        page_numbers: Optional list of 1-indexed page numbers to extract. If None, extracts all.
        
    Returns:
        Extracted text formatted with page headings.
    """
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    text_chunks = []

    for idx, page in enumerate(reader.pages):
        p_num = idx + 1
        if page_numbers is None or p_num in page_numbers:
            content = page.extract_text() or ""
            text_chunks.append(f"<!-- Page {p_num} of {total_pages} -->\n{content.strip()}\n")

    return "\n".join(text_chunks).strip()

