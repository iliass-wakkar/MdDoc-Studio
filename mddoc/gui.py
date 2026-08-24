"""
Native Desktop GUI for MdDoc.
Runs with zero terminal window using Tkinter / TTK.
"""

import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Ensure repo root is on sys.path for direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from .themes import THEMES, get_theme
    from .native_converter import parse_frontmatter, convert_markdown_to_docx
    from .pandoc_converter import convert_with_pandoc, is_pandoc_available
except (ImportError, ValueError):
    from mddoc.themes import THEMES, get_theme
    from mddoc.native_converter import parse_frontmatter, convert_markdown_to_docx
    from mddoc.pandoc_converter import convert_with_pandoc, is_pandoc_available


class MdDocGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MdDoc — Markdown to Beautiful DOCX")
        self.root.geometry("680x720")
        self.root.minsize(620, 650)
        
        # Set Window Icon
        self._set_window_icon()

        # Windows theme styling
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self._configure_styles()
        self._create_widgets()

    def _set_window_icon(self):
        """Set window icon if available."""
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico"),
            os.path.join(os.path.dirname(__file__), "..", "icon.ico"),
            "icon.ico",
            "assets/icon.ico"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                try:
                    self.root.iconbitmap(p)
                    break
                except Exception:
                    pass

    def _configure_styles(self):
        """Setup custom TTK styles."""
        self.root.configure(bg="#F8FAFC")
        
        self.style.configure(".", font=("Segoe UI", 9), background="#F8FAFC")
        self.style.configure("Header.TLabel", font=("Segoe UI Semibold", 16), foreground="#1E3A5F", background="#F8FAFC")
        self.style.configure("Subheader.TLabel", font=("Segoe UI", 9), foreground="#64748B", background="#F8FAFC")
        self.style.configure("Section.TLabelframe", background="#FFFFFF")
        self.style.configure("Section.TLabelframe.Label", font=("Segoe UI Semibold", 10), foreground="#1E3A5F", background="#F8FAFC")
        
        self.style.configure("Primary.TButton", font=("Segoe UI Semibold", 10), foreground="#FFFFFF", background="#1E3A5F", padding=8)
        self.style.map("Primary.TButton", background=[("active", "#2E5A7E"), ("disabled", "#94A3B8")])

        self.style.configure("Secondary.TButton", font=("Segoe UI", 9), foreground="#1E3A5F", background="#E2E8F0", padding=6)
        self.style.map("Secondary.TButton", background=[("active", "#CBD5E1")])

    def _create_widgets(self):
        main_container = ttk.Frame(self.root, padding="16 16 16 16")
        main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Header Banner
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 12))
        
        lbl_title = ttk.Label(header_frame, text="📄 MdDoc Document Studio", style="Header.TLabel")
        lbl_title.pack(anchor=tk.W)
        
        lbl_desc = ttk.Label(
            header_frame,
            text="Convert Markdown into publication-ready Word documents with professional styling.",
            style="Subheader.TLabel"
        )
        lbl_desc.pack(anchor=tk.W, pady=(2, 0))

        # 2. File Selection Section
        file_frame = ttk.LabelFrame(main_container, text="  1. Markdown Input File  ", style="Section.TLabelframe", padding=12)
        file_frame.pack(fill=tk.X, pady=6)

        file_row = ttk.Frame(file_frame)
        file_row.pack(fill=tk.X)

        self.var_input_file = tk.StringVar()
        self.entry_input = ttk.Entry(file_row, textvariable=self.var_input_file, font=("Segoe UI", 9))
        self.entry_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        btn_browse = ttk.Button(file_row, text="Browse...", style="Secondary.TButton", command=self._browse_input_file)
        btn_browse.pack(side=tk.RIGHT)

        # Output file row
        out_row = ttk.Frame(file_frame)
        out_row.pack(fill=tk.X, pady=(8, 0))

        ttk.Label(out_row, text="Output DOCX:").pack(side=tk.LEFT, padx=(0, 6))
        self.var_output_file = tk.StringVar()
        self.entry_output = ttk.Entry(out_row, textvariable=self.var_output_file, font=("Segoe UI", 9))
        self.entry_output.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        btn_out_browse = ttk.Button(out_row, text="Save As...", style="Secondary.TButton", command=self._browse_output_file)
        btn_out_browse.pack(side=tk.RIGHT)

        # 3. Theme & Engine Settings Section
        theme_frame = ttk.LabelFrame(main_container, text="  2. Design Theme & Engine  ", style="Section.TLabelframe", padding=12)
        theme_frame.pack(fill=tk.X, pady=6)

        t_row = ttk.Frame(theme_frame)
        t_row.pack(fill=tk.X)

        ttk.Label(t_row, text="Color Theme:").grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=4)
        self.var_theme = tk.StringVar(value="modern")
        self.combo_theme = ttk.Combobox(
            t_row,
            textvariable=self.var_theme,
            values=["modern", "nordic", "academic", "forest", "corporate"],
            state="readonly",
            width=18
        )
        self.combo_theme.grid(row=0, column=1, sticky=tk.W, pady=4)
        self.combo_theme.bind("<<ComboboxSelected>>", self._on_theme_changed)

        ttk.Label(t_row, text="Engine:").grid(row=0, column=2, sticky=tk.W, padx=(16, 8), pady=4)
        self.var_engine = tk.StringVar(value="auto")
        self.combo_engine = ttk.Combobox(
            t_row,
            textvariable=self.var_engine,
            values=["auto", "native", "pandoc"],
            state="readonly",
            width=12
        )
        self.combo_engine.grid(row=0, column=3, sticky=tk.W, pady=4)

        # Theme Description Preview
        self.lbl_theme_desc = ttk.Label(
            theme_frame,
            text="Modern Tech — Deep navy headings, teal accents, and soft slate text.",
            font=("Segoe UI", 8, "italic"),
            foreground="#475569"
        )
        self.lbl_theme_desc.pack(anchor=tk.W, pady=(6, 0))

        # 4. Document Options Section
        opts_frame = ttk.LabelFrame(main_container, text="  3. Document Structure & Options  ", style="Section.TLabelframe", padding=12)
        opts_frame.pack(fill=tk.X, pady=6)

        chk_row = ttk.Frame(opts_frame)
        chk_row.pack(fill=tk.X)

        self.var_cover = tk.BooleanVar(value=True)
        self.chk_cover = ttk.Checkbutton(chk_row, text="Include Cover Page", variable=self.var_cover)
        self.chk_cover.pack(side=tk.LEFT, padx=(0, 16))

        self.var_toc = tk.BooleanVar(value=True)
        self.chk_toc = ttk.Checkbutton(chk_row, text="Include Table of Contents", variable=self.var_toc)
        self.chk_toc.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(chk_row, text="Page Size:").pack(side=tk.LEFT, padx=(12, 6))
        self.var_pagesize = tk.StringVar(value="A4")
        self.combo_pagesize = ttk.Combobox(chk_row, textvariable=self.var_pagesize, values=["A4", "Letter"], state="readonly", width=8)
        self.combo_pagesize.pack(side=tk.LEFT)

        # Metadata Overrides Grid
        meta_grid = ttk.Frame(opts_frame)
        meta_grid.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(meta_grid, text="Title (opt):").grid(row=0, column=0, sticky=tk.W, padx=(0, 6), pady=2)
        self.var_title = tk.StringVar()
        self.entry_title = ttk.Entry(meta_grid, textvariable=self.var_title, font=("Segoe UI", 9))
        self.entry_title.grid(row=0, column=1, sticky=tk.EW, padx=(0, 12), pady=2)

        ttk.Label(meta_grid, text="Subtitle (opt):").grid(row=0, column=2, sticky=tk.W, padx=(0, 6), pady=2)
        self.var_subtitle = tk.StringVar()
        self.entry_subtitle = ttk.Entry(meta_grid, textvariable=self.var_subtitle, font=("Segoe UI", 9))
        self.entry_subtitle.grid(row=0, column=3, sticky=tk.EW, pady=2)

        ttk.Label(meta_grid, text="Author (opt):").grid(row=1, column=0, sticky=tk.W, padx=(0, 6), pady=2)
        self.var_author = tk.StringVar()
        self.entry_author = ttk.Entry(meta_grid, textvariable=self.var_author, font=("Segoe UI", 9))
        self.entry_author.grid(row=1, column=1, sticky=tk.EW, padx=(0, 12), pady=2)

        ttk.Label(meta_grid, text="Date (opt):").grid(row=1, column=2, sticky=tk.W, padx=(0, 6), pady=2)
        self.var_date = tk.StringVar()
        self.entry_date = ttk.Entry(meta_grid, textvariable=self.var_date, font=("Segoe UI", 9))
        self.entry_date.grid(row=1, column=3, sticky=tk.EW, pady=2)

        meta_grid.columnconfigure(1, weight=1)
        meta_grid.columnconfigure(3, weight=1)

        # 5. Action & Status Section
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=tk.X, pady=(14, 0))

        self.btn_convert = ttk.Button(
            action_frame,
            text="✨ Convert to Beautiful DOCX",
            style="Primary.TButton",
            command=self._start_conversion
        )
        self.btn_convert.pack(fill=tk.X, ipady=4)

        # Status Label
        self.var_status = tk.StringVar(value="Ready. Select a Markdown file to begin.")
        self.lbl_status = ttk.Label(
            action_frame,
            textvariable=self.var_status,
            font=("Segoe UI", 9),
            foreground="#1E3A5F"
        )
        self.lbl_status.pack(anchor=tk.W, pady=(8, 4))

        # Result Action Buttons (Hidden until generated)
        self.result_frame = ttk.Frame(action_frame)
        self.result_frame.pack(fill=tk.X, pady=(4, 0))

        self.btn_open_word = ttk.Button(
            self.result_frame,
            text="📂 Open in Word",
            style="Secondary.TButton",
            command=self._open_in_word
        )
        self.btn_open_word.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_open_dir = ttk.Button(
            self.result_frame,
            text="📁 Show in File Explorer",
            style="Secondary.TButton",
            command=self._open_in_explorer
        )
        self.btn_open_dir.pack(side=tk.LEFT)

        self.last_generated_path = None
        self.result_frame.pack_forget()  # Hide initially

    def _on_theme_changed(self, event=None):
        theme_name = self.var_theme.get()
        theme_info = get_theme(theme_name)
        self.lbl_theme_desc.config(text=f"{theme_info['name']} — {theme_info['description']}")

    def _browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Markdown File",
            filetypes=[("Markdown Files", "*.md;*.markdown;*.mdown"), ("All Files", "*.*")]
        )
        if file_path:
            self.var_input_file.set(file_path)
            # Default output path
            base, _ = os.path.splitext(file_path)
            self.var_output_file.set(base + ".docx")

            # Try reading frontmatter to pre-fill metadata
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                fm, _ = parse_frontmatter(content)
                if "title" in fm:
                    self.var_title.set(str(fm["title"]))
                if "subtitle" in fm:
                    self.var_subtitle.set(str(fm["subtitle"]))
                if "author" in fm:
                    self.var_author.set(str(fm["author"]))
                if "date" in fm:
                    self.var_date.set(str(fm["date"]))
                if "theme" in fm and fm["theme"].lower() in THEMES:
                    self.var_theme.set(fm["theme"].lower())
                    self._on_theme_changed()
            except Exception:
                pass

    def _browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Output DOCX",
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx")]
        )
        if file_path:
            self.var_output_file.set(file_path)

    def _start_conversion(self):
        input_path = self.var_input_file.get().strip()
        if not input_path or not os.path.exists(input_path):
            messagebox.showwarning("Missing Input", "Please select a valid Markdown file first.")
            return

        out_path = self.var_output_file.get().strip()
        if not out_path:
            base, _ = os.path.splitext(input_path)
            out_path = base + ".docx"
            self.var_output_file.set(out_path)

        self.btn_convert.config(state="disabled")
        self.var_status.set("⏳ Converting document, please wait...")
        self.result_frame.pack_forget()

        # Run conversion in a worker thread to keep GUI responsive
        threading.Thread(target=self._run_conversion_worker, args=(input_path, out_path), daemon=True).start()

    def _run_conversion_worker(self, input_path: str, out_path: str):
        theme_name = self.var_theme.get()
        engine = self.var_engine.get()
        title = self.var_title.get().strip() or None
        subtitle = self.var_subtitle.get().strip() or None
        author = self.var_author.get().strip() or None
        date = self.var_date.get().strip() or None
        show_cover = self.var_cover.get()
        show_toc = self.var_toc.get()
        page_size = self.var_pagesize.get()

        try:
            chosen_engine = engine.lower()
            if chosen_engine == "auto":
                chosen_engine = "pandoc" if is_pandoc_available() else "native"

            if chosen_engine == "pandoc":
                try:
                    res = convert_with_pandoc(
                        input_path=input_path,
                        output_path=out_path,
                        theme_name=theme_name,
                        toc=show_toc
                    )
                except Exception:
                    # Fallback to native
                    res = convert_markdown_to_docx(
                        input_path=input_path,
                        output_path=out_path,
                        theme_name=theme_name,
                        title=title,
                        subtitle=subtitle,
                        author=author,
                        date=date,
                        show_cover=show_cover,
                        show_toc=show_toc,
                        page_size=page_size
                    )
            else:
                res = convert_markdown_to_docx(
                    input_path=input_path,
                    output_path=out_path,
                    theme_name=theme_name,
                    title=title,
                    subtitle=subtitle,
                    author=author,
                    date=date,
                    show_cover=show_cover,
                    show_toc=show_toc,
                    page_size=page_size
                )

            self.last_generated_path = res
            self.root.after(0, self._on_conversion_success, res)
        except Exception as e:
            self.root.after(0, self._on_conversion_error, str(e))

    def _on_conversion_success(self, output_file: str):
        self.btn_convert.config(state="normal")
        self.var_status.set(f"✔ Success! Generated: {os.path.basename(output_file)}")
        self.result_frame.pack(fill=tk.X, pady=(4, 0))

    def _on_conversion_error(self, err_msg: str):
        self.btn_convert.config(state="normal")
        self.var_status.set(f"❌ Error during conversion.")
        messagebox.showerror("Conversion Failed", f"An error occurred:\n\n{err_msg}")

    def _open_in_word(self):
        if self.last_generated_path and os.path.exists(self.last_generated_path):
            os.startfile(self.last_generated_path)

    def _open_in_explorer(self):
        if self.last_generated_path and os.path.exists(self.last_generated_path):
            subprocess.run(f'explorer /select,"{os.path.abspath(self.last_generated_path)}"', shell=True)


def launch_gui():
    """Start Tkinter desktop application."""
    root = tk.Tk()
    app = MdDocGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
