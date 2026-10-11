"""
Lightweight, Permissive PDF Utilities for MdDoc Studio.
Uses pypdf (BSD-3-Clause) and pypdfium2 (BSD/Apache-2.0).
Zero AGPL licensing traps. 100% offline and safe for commercial/distribution use.
"""

import os
from typing import List, Optional, Tuple
from pypdf import PdfReader, PdfWriter
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
    output_pdf_path: str
) -> str:
    """
    Convert a list of images (PNG, JPG, WEBP) into a single standard PDF.
    
    Args:
        image_paths: List of paths to source images.
        output_pdf_path: Target path for the output PDF.
        
    Returns:
        Path to generated PDF file.
    """
    if not image_paths:
        raise ValueError("At least one image path must be provided.")

    from PIL import Image

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)

    pil_images = []
    for p in image_paths:
        img = Image.open(p)
        # Convert to RGB (in case of PNG with transparency / RGBA)
        if img.mode in ("RGBA", "LA", "P"):
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            pil_images.append(rgb_img)
        else:
            pil_images.append(img.convert("RGB"))

    first = pil_images[0]
    rest = pil_images[1:] if len(pil_images) > 1 else []
    first.save(output_pdf_path, "PDF", resolution=100.0, save_all=True, append_images=rest)

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
