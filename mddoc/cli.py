"""
Command Line Interface for MdDoc.
"""

import argparse
import os
import sys
import time
from typing import Optional

from .themes import THEMES, get_theme
from .templates import generate_all_reference_templates, find_pandoc_executable
from .pandoc_converter import convert_with_pandoc, is_pandoc_available
from .native_converter import convert_markdown_to_docx


def print_themes_table():
    """Print available themes with color and typography details."""
    print("\n" + "=" * 70)
    print(f"{'THEME NAME':<14} | {'HEADING FONT':<14} | {'PRIMARY':<8} | {'DESCRIPTION'}")
    print("-" * 70)
    for key, val in THEMES.items():
        print(f"{key:<14} | {val['font_heading']:<14} | #{val['primary']:<7} | {val['description']}")
    print("=" * 70 + "\n")


def run_conversion(
    input_file: str,
    output_file: Optional[str] = None,
    theme: str = "modern",
    engine: str = "auto",
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    author: Optional[str] = None,
    date: Optional[str] = None,
    show_cover: bool = True,
    show_toc: bool = True,
    page_size: str = "A4"
) -> str:
    """Execute document conversion with selected or auto engine."""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    if output_file is None:
        base = os.path.splitext(input_file)[0]
        output_file = base + ".docx"

    chosen_engine = engine.lower()
    if chosen_engine == "auto":
        chosen_engine = "pandoc" if is_pandoc_available() else "native"

    if chosen_engine == "pandoc":
        try:
            out = convert_with_pandoc(
                input_path=input_file,
                output_path=output_file,
                theme_name=theme,
                toc=show_toc
            )
            print(f"[Engine: Pandoc] Generated -> {out}")
            return out
        except Exception as e:
            print(f"[Warning] Pandoc conversion failed ({e}). Falling back to Native Engine...")
            chosen_engine = "native"

    if chosen_engine == "native":
        out = convert_markdown_to_docx(
            input_path=input_file,
            output_path=output_file,
            theme_name=theme,
            title=title,
            subtitle=subtitle,
            author=author,
            date=date,
            show_cover=show_cover,
            show_toc=show_toc,
            page_size=page_size
        )
        print(f"[Engine: Native Python] Generated -> {out}")
        return out

    raise ValueError(f"Unknown engine: {engine}")


def watch_file(input_file: str, **kwargs):
    """Continuously monitor input file and re-run conversion on modification."""
    print(f"[*] Watching '{input_file}' for changes (Ctrl+C to stop)...")
    last_mtime = os.path.getmtime(input_file)
    run_conversion(input_file, **kwargs)

    try:
        while True:
            time.sleep(1.0)
            if os.path.exists(input_file):
                current_mtime = os.path.getmtime(input_file)
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    print(f"\n[!] File modified at {time.strftime('%H:%M:%S')}. Rebuilding...")
                    try:
                        run_conversion(input_file, **kwargs)
                    except Exception as err:
                        print(f"[Error] Rebuild failed: {err}")
    except KeyboardInterrupt:
        print("\n[*] Stopped watch mode.")


def main():
    parser = argparse.ArgumentParser(
        prog="mddoc",
        description="MdDoc - Markdown to Beautiful, Publication-Quality DOCX Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mddoc report.md -o report.docx
  mddoc report.md --theme nordic --author "John Doe"
  mddoc report.md --theme academic --engine native
  mddoc report.md --watch
  mddoc --list-themes
  mddoc --build-templates
        """
    )
    parser.add_argument("input", nargs="?", help="Input Markdown (.md) file")
    parser.add_argument("-o", "--output", help="Output DOCX file path")
    parser.add_argument("--theme", choices=list(THEMES.keys()), default="modern",
                        help="Color theme (default: modern)")
    parser.add_argument("--engine", choices=["auto", "pandoc", "native"], default="auto",
                        help="Conversion engine (default: auto - pandoc if available, else native)")
    parser.add_argument("--title", help="Document title (overrides frontmatter and H1)")
    parser.add_argument("--subtitle", help="Document subtitle")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--date", help="Document date")
    parser.add_argument("--no-cover", action="store_true", help="Disable cover page generation")
    parser.add_argument("--no-toc", action="store_true", help="Disable Table of Contents")
    parser.add_argument("--page-size", choices=["A4", "Letter"], default="A4", help="Page format (default: A4)")
    parser.add_argument("--gui", action="store_true", help="Launch native desktop GUI window")
    parser.add_argument("--web", action="store_true", help="Launch interactive browser Web Studio")
    parser.add_argument("--watch", action="store_true", help="Watch input file and auto-rebuild on save")
    parser.add_argument("--list-themes", action="store_true", help="List all available themes and exits")
    parser.add_argument("--build-templates", action="store_true", help="Pre-build reference docx templates for all themes")

    args = parser.parse_args()

    if args.gui:
        from .gui import launch_gui
        launch_gui()
        sys.exit(0)

    if args.web:
        from .web_server import launch_web_ui
        launch_web_ui()
        sys.exit(0)

    if args.list_themes:
        print_themes_table()
        sys.exit(0)

    if args.build_templates:
        print("[*] Generating reference docx templates for all themes...")
        res = generate_all_reference_templates()
        for theme_name, t_path in res.items():
            print(f"  + {theme_name:<12} -> {t_path}")
        print("[OK] All reference templates created successfully in templates/ directory.\n")
        sys.exit(0)

    if not args.input:
        parser.print_help()
        sys.exit(1)

    kwargs = {
        "output_file": args.output,
        "theme": args.theme,
        "engine": args.engine,
        "title": args.title,
        "subtitle": args.subtitle,
        "author": args.author,
        "date": args.date,
        "show_cover": not args.no_cover,
        "show_toc": not args.no_toc,
        "page_size": args.page_size,
    }

    if args.watch:
        watch_file(args.input, **kwargs)
    else:
        run_conversion(args.input, **kwargs)


if __name__ == "__main__":
    main()
