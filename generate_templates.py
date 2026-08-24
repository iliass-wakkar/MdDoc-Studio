#!/usr/bin/env python3
"""
Generate Reference DOCX templates for all themes in MdDoc.
"""

from mddoc.templates import generate_all_reference_templates

if __name__ == "__main__":
    print("Generating reference DOCX templates for all themes...")
    templates = generate_all_reference_templates()
    for theme_name, path in templates.items():
        print(f"  [OK] {theme_name.upper():<12} -> {path}")
    print("\nDone! Reference templates are ready to use with Pandoc or as standalone templates.")
