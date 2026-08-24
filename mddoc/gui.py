"""
Native Desktop GUI for MdDoc Studio.
Runs with zero terminal window using Tkinter / TTK.
Features multi-tab layout, custom theme designer with color pickers, and developer profile.
"""

import os
import sys
import threading
import subprocess
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from .themes import THEMES, get_theme, create_custom_theme
    from .native_converter import parse_frontmatter, convert_markdown_to_docx
    from .pandoc_converter import convert_with_pandoc, is_pandoc_available
except (ImportError, ValueError):
    from mddoc.themes import THEMES, get_theme, create_custom_theme
    from mddoc.native_converter import parse_frontmatter, convert_markdown_to_docx
    from mddoc.pandoc_converter import convert_with_pandoc, is_pandoc_available


SAMPLE_MD_TEXT = """---
title: "MdDoc Architecture & Specification"
subtitle: "High-Performance Markdown to Publication-Quality Word DOCX"
author: "Engineering Team"
date: "August 2026"
theme: "modern"
toc: true
cover_page: true
---

# Executive Summary

**MdDoc** is a standalone, 100% offline desktop and web application designed to convert standard Markdown into publication-quality Microsoft Word documents (`.docx`).

> "Good typography makes documents effortless to read and impactful to deliver."

---

# Key Features

| Feature | Capability | Status |
|---|---|---|
| **5 Curated Themes + Custom** | Modern, Nordic, Academic, Forest, Corporate, Custom | Active |
| **Cover Page Generator** | Clean typography & accent geometry | Included |
| **Table Formatting** | Booktabs style with zebra striping | Enabled |
| **GFM Admonitions** | Styled note & warning callout boxes | Supported |

## Callout Alerts

> [!NOTE]
> This document was generated using MdDoc Studio Desktop Engine.

> [!TIP]
> Customize fonts and colors in the "Themes & Colors" tab!
"""


class MdDocGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MdDoc Studio — Markdown to Beautiful DOCX")
        self.root.geometry("760x820")
        self.root.minsize(700, 750)
        
        # Custom Theme State
        self.custom_primary = "#7C3AED"
        self.custom_secondary = "#EC4899"
        self.custom_accent = "#F59E0B"

        self._set_window_icon()
        self._configure_styles()
        self._create_layout()

    def _set_window_icon(self):
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
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.root.configure(bg="#F8FAFC")
        
        # Base colors
        self.style.configure(".", font=("Segoe UI", 9), background="#F8FAFC")
        self.style.configure("TNotebook", background="#F8FAFC", borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI Semibold", 10), padding=[14, 6], background="#E2E8F0", foreground="#475569")
        self.style.map("TNotebook.Tab", background=[("selected", "#FFFFFF")], foreground=[("selected", "#1E3A5F")])

        self.style.configure("Card.TLabelframe", background="#FFFFFF", bordercolor="#E2E8F0", relief="solid", borderwidth=1)
        self.style.configure("Card.TLabelframe.Label", font=("Segoe UI Semibold", 10), foreground="#1E3A5F", background="#FFFFFF")

        self.style.configure("Primary.TButton", font=("Segoe UI Semibold", 11), foreground="#FFFFFF", background="#1E3A5F", padding=[16, 10])
        self.style.map("Primary.TButton", background=[("active", "#2E5A7E"), ("disabled", "#94A3B8")])

        self.style.configure("Accent.TButton", font=("Segoe UI Semibold", 9), foreground="#FFFFFF", background="#2E8B8B", padding=[10, 5])
        self.style.map("Accent.TButton", background=[("active", "#236B6B")])

        self.style.configure("Secondary.TButton", font=("Segoe UI", 9), foreground="#1E3A5F", background="#E2E8F0", padding=[10, 5])
        self.style.map("Secondary.TButton", background=[("active", "#CBD5E1")])

    def _create_layout(self):
        # 1. Modern Header Bar
        header_bar = tk.Frame(self.root, bg="#1E3A5F", height=64)
        header_bar.pack(fill=tk.X)

        header_inner = tk.Frame(header_bar, bg="#1E3A5F", padx=16, pady=12)
        header_inner.pack(fill=tk.X)

        title_frame = tk.Frame(header_inner, bg="#1E3A5F")
        title_frame.pack(side=tk.LEFT)

        lbl_app_title = tk.Label(title_frame, text="📄 MdDoc Studio", font=("Segoe UI Semibold", 16), fg="#FFFFFF", bg="#1E3A5F")
        lbl_app_title.pack(anchor=tk.W)

        lbl_app_sub = tk.Label(title_frame, text="Markdown to Publication-Quality Word DOCX", font=("Segoe UI", 9), fg="#94A3B8", bg="#1E3A5F")
        lbl_app_sub.pack(anchor=tk.W)

        btn_web = tk.Button(
            header_inner,
            text="🌐 Open Web Studio",
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg="#2E8B8B",
            activebackground="#236B6B",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._launch_web_studio
        )
        btn_web.pack(side=tk.RIGHT, pady=4)

        # 2. Main Content Notebook Tabs
        main_frame = tk.Frame(self.root, bg="#F8FAFC", padx=14, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Tab 1: Document & Editor
        self.tab_doc = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_doc, text="  📝 Document & Content  ")
        self._build_doc_tab()

        # Tab 2: Themes & Custom Palette
        self.tab_theme = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_theme, text="  🎨 Themes & Custom Colors  ")
        self._build_theme_tab()

        # Tab 3: About & Developer
        self.tab_about = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_about, text="  👨‍💻 Developer & About  ")
        self._build_about_tab()

        # 3. Bottom Action Bar
        bottom_card = tk.Frame(self.root, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1, padx=16, pady=12)
        bottom_card.pack(fill=tk.X, side=tk.BOTTOM, padx=14, pady=(0, 14))

        self.btn_convert = ttk.Button(
            bottom_card,
            text="⬇️ Convert & Save Word Document (.docx)",
            style="Primary.TButton",
            command=self._start_conversion
        )
        self.btn_convert.pack(fill=tk.X)

        self.var_status = tk.StringVar(value="Ready. Select a file or write Markdown to begin.")
        self.lbl_status = tk.Label(bottom_card, textvariable=self.var_status, font=("Segoe UI", 9), fg="#1E3A5F", bg="#FFFFFF")
        self.lbl_status.pack(anchor=tk.W, pady=(6, 0))

        # Success Action Buttons (Open in Word / Explorer)
        self.result_frame = tk.Frame(bottom_card, bg="#FFFFFF")
        self.result_frame.pack(fill=tk.X, pady=(6, 0))

        self.btn_open_word = ttk.Button(
            self.result_frame,
            text="📂 Open in Word",
            style="Accent.TButton",
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
        self.result_frame.pack_forget()

    def _build_doc_tab(self):
        # 1. File Selector Card
        file_card = ttk.LabelFrame(self.tab_doc, text=" 1. Markdown Source File ", style="Card.TLabelframe", padding=10)
        file_card.pack(fill=tk.X, pady=(0, 8))

        row1 = ttk.Frame(file_card)
        row1.pack(fill=tk.X)

        self.var_input_file = tk.StringVar()
        entry_input = ttk.Entry(row1, textvariable=self.var_input_file, font=("Segoe UI", 9))
        entry_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_browse = ttk.Button(row1, text="📂 Browse...", style="Secondary.TButton", command=self._browse_input_file)
        btn_browse.pack(side=tk.LEFT, padx=(0, 6))

        btn_sample = ttk.Button(row1, text="📋 Load Sample", style="Secondary.TButton", command=self._load_sample)
        btn_sample.pack(side=tk.LEFT, padx=(0, 6))

        btn_clear = ttk.Button(row1, text="🗑️ Clear", style="Secondary.TButton", command=self._clear_content)
        btn_clear.pack(side=tk.LEFT)

        # Output DOCX Row
        row2 = ttk.Frame(file_card)
        row2.pack(fill=tk.X, pady=(8, 0))

        ttk.Label(row2, text="Save As:").pack(side=tk.LEFT, padx=(0, 6))
        self.var_output_file = tk.StringVar()
        entry_output = ttk.Entry(row2, textvariable=self.var_output_file, font=("Segoe UI", 9))
        entry_output.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_out_browse = ttk.Button(row2, text="💾 Save Location...", style="Secondary.TButton", command=self._browse_output_file)
        btn_out_browse.pack(side=tk.RIGHT)

        # 2. Markdown Editor Box
        editor_card = ttk.LabelFrame(self.tab_doc, text=" 2. Markdown Editor / Viewer ", style="Card.TLabelframe", padding=10)
        editor_card.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.txt_editor = tk.Text(
            editor_card,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#FCFDFE",
            fg="#0F172A",
            insertbackground="#1E3A5F",
            relief="solid",
            borderwidth=1,
            height=10
        )
        self.txt_editor.pack(fill=tk.BOTH, expand=True)
        self.txt_editor.insert(tk.END, SAMPLE_MD_TEXT)

        # 3. Document Structure & Metadata
        meta_card = ttk.LabelFrame(self.tab_doc, text=" 3. Document Structure & Metadata ", style="Card.TLabelframe", padding=10)
        meta_card.pack(fill=tk.X)

        chk_row = ttk.Frame(meta_card)
        chk_row.pack(fill=tk.X, pady=(0, 6))

        self.var_cover = tk.BooleanVar(value=True)
        ttk.Checkbutton(chk_row, text="Cover Page", variable=self.var_cover).pack(side=tk.LEFT, padx=(0, 16))

        self.var_toc = tk.BooleanVar(value=True)
        ttk.Checkbutton(chk_row, text="Table of Contents", variable=self.var_toc).pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(chk_row, text="Page Size:").pack(side=tk.LEFT, padx=(10, 4))
        self.var_pagesize = tk.StringVar(value="A4")
        combo_size = ttk.Combobox(chk_row, textvariable=self.var_pagesize, values=["A4", "Letter"], state="readonly", width=8)
        combo_size.pack(side=tk.LEFT)

        meta_grid = ttk.Frame(meta_card)
        meta_grid.pack(fill=tk.X)

        ttk.Label(meta_grid, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=(0, 4), pady=2)
        self.var_title = tk.StringVar()
        ttk.Entry(meta_grid, textvariable=self.var_title).grid(row=0, column=1, sticky=tk.EW, padx=(0, 10), pady=2)

        ttk.Label(meta_grid, text="Author:").grid(row=0, column=2, sticky=tk.W, padx=(0, 4), pady=2)
        self.var_author = tk.StringVar()
        ttk.Entry(meta_grid, textvariable=self.var_author).grid(row=0, column=3, sticky=tk.EW, pady=2)

        ttk.Label(meta_grid, text="Subtitle:").grid(row=1, column=0, sticky=tk.W, padx=(0, 4), pady=2)
        self.var_subtitle = tk.StringVar()
        ttk.Entry(meta_grid, textvariable=self.var_subtitle).grid(row=1, column=1, sticky=tk.EW, padx=(0, 10), pady=2)

        ttk.Label(meta_grid, text="Date:").grid(row=1, column=2, sticky=tk.W, padx=(0, 4), pady=2)
        self.var_date = tk.StringVar()
        ttk.Entry(meta_grid, textvariable=self.var_date).grid(row=1, column=3, sticky=tk.EW, pady=2)

        meta_grid.columnconfigure(1, weight=1)
        meta_grid.columnconfigure(3, weight=1)

    def _build_theme_tab(self):
        # 1. Curated Themes
        curated_card = ttk.LabelFrame(self.tab_theme, text=" Curated Design Palettes ", style="Card.TLabelframe", padding=12)
        curated_card.pack(fill=tk.X, pady=(0, 10))

        t_row = ttk.Frame(curated_card)
        t_row.pack(fill=tk.X)

        ttk.Label(t_row, text="Select Theme:").pack(side=tk.LEFT, padx=(0, 8))
        self.var_theme = tk.StringVar(value="modern")
        self.combo_theme = ttk.Combobox(
            t_row,
            textvariable=self.var_theme,
            values=["modern", "nordic", "academic", "forest", "corporate", "custom"],
            state="readonly",
            width=20
        )
        self.combo_theme.pack(side=tk.LEFT, padx=(0, 14))
        self.combo_theme.bind("<<ComboboxSelected>>", self._on_theme_selection)

        self.lbl_theme_desc = ttk.Label(
            curated_card,
            text="Modern Tech — Cambria/Calibri typography, Deep navy headings, teal accents.",
            font=("Segoe UI", 9, "italic"),
            foreground="#475569"
        )
        self.lbl_theme_desc.pack(anchor=tk.W, pady=(8, 0))

        # 2. Custom Palette Designer
        self.custom_card = ttk.LabelFrame(self.tab_theme, text=" ✨ Custom Theme Designer ", style="Card.TLabelframe", padding=12)
        self.custom_card.pack(fill=tk.BOTH, expand=True)

        # Preset Quick Chips
        preset_row = ttk.Frame(self.custom_card)
        preset_row.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(preset_row, text="Quick Presets:").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(preset_row, text="💜 Violet", style="Secondary.TButton", command=lambda: self._apply_preset("violet")).pack(side=tk.LEFT, padx=3)
        ttk.Button(preset_row, text="🌅 Sunset", style="Secondary.TButton", command=lambda: self._apply_preset("sunset")).pack(side=tk.LEFT, padx=3)
        ttk.Button(preset_row, text="🍃 Emerald", style="Secondary.TButton", command=lambda: self._apply_preset("emerald")).pack(side=tk.LEFT, padx=3)
        ttk.Button(preset_row, text="☕ Amber", style="Secondary.TButton", command=lambda: self._apply_preset("amber")).pack(side=tk.LEFT, padx=3)

        # Color Pickers Row
        pickers_frame = ttk.Frame(self.custom_card)
        pickers_frame.pack(fill=tk.X, pady=(0, 14))

        # Primary Picker
        f_p = tk.Frame(pickers_frame, bg="#FFFFFF", highlightbackground="#CBD5E1", highlightthickness=1, padx=8, pady=8)
        f_p.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(f_p, text="Primary (H1):", font=("Segoe UI Semibold", 9), bg="#FFFFFF").pack(anchor=tk.W)
        self.swatch_p = tk.Label(f_p, text="   ", bg=self.custom_primary, relief="solid", borderwidth=1, width=4)
        self.swatch_p.pack(side=tk.LEFT, padx=(0, 6), pady=4)
        self.var_hex_p = tk.StringVar(value=self.custom_primary)
        ttk.Entry(f_p, textvariable=self.var_hex_p, width=8).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(f_p, text="Pick", width=4, command=lambda: self._pick_color('primary')).pack(side=tk.LEFT)

        # Secondary Picker
        f_s = tk.Frame(pickers_frame, bg="#FFFFFF", highlightbackground="#CBD5E1", highlightthickness=1, padx=8, pady=8)
        f_s.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(f_s, text="Secondary (Accent):", font=("Segoe UI Semibold", 9), bg="#FFFFFF").pack(anchor=tk.W)
        self.swatch_s = tk.Label(f_s, text="   ", bg=self.custom_secondary, relief="solid", borderwidth=1, width=4)
        self.swatch_s.pack(side=tk.LEFT, padx=(0, 6), pady=4)
        self.var_hex_s = tk.StringVar(value=self.custom_secondary)
        ttk.Entry(f_s, textvariable=self.var_hex_s, width=8).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(f_s, text="Pick", width=4, command=lambda: self._pick_color('secondary')).pack(side=tk.LEFT)

        # Highlight Picker
        f_a = tk.Frame(pickers_frame, bg="#FFFFFF", highlightbackground="#CBD5E1", highlightthickness=1, padx=8, pady=8)
        f_a.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(f_a, text="Highlight:", font=("Segoe UI Semibold", 9), bg="#FFFFFF").pack(anchor=tk.W)
        self.swatch_a = tk.Label(f_a, text="   ", bg=self.custom_accent, relief="solid", borderwidth=1, width=4)
        self.swatch_a.pack(side=tk.LEFT, padx=(0, 6), pady=4)
        self.var_hex_a = tk.StringVar(value=self.custom_accent)
        ttk.Entry(f_a, textvariable=self.var_hex_a, width=8).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(f_a, text="Pick", width=4, command=lambda: self._pick_color('accent')).pack(side=tk.LEFT)

        # Font Selectors
        font_row = ttk.Frame(self.custom_card)
        font_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(font_row, text="Heading Font:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_font_head = tk.StringVar(value="Georgia")
        combo_fhead = ttk.Combobox(font_row, textvariable=self.var_font_head, values=["Georgia", "Cambria", "Segoe UI", "Arial", "Garamond", "Trebuchet MS", "Times New Roman"], state="readonly", width=14)
        combo_fhead.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(font_row, text="Body Font:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_font_body = tk.StringVar(value="Calibri")
        combo_fbody = ttk.Combobox(font_row, textvariable=self.var_font_body, values=["Calibri", "Segoe UI", "Georgia", "Arial", "Garamond", "Times New Roman"], state="readonly", width=14)
        combo_fbody.pack(side=tk.LEFT)

    def _build_about_tab(self):
        container = tk.Frame(self.tab_about, bg="#F8FAFC")
        container.pack(fill=tk.BOTH, expand=True)

        # Developer Profile Card
        dev_card = tk.Frame(container, bg="#0F172A", padx=20, pady=18, highlightbackground="#334155", highlightthickness=1)
        dev_card.pack(fill=tk.X, pady=(0, 12))

        tk.Label(dev_card, text="👨‍💻 Developer Profile", font=("Segoe UI Semibold", 10), fg="#38BDF8", bg="#0F172A").pack(anchor=tk.W)
        tk.Label(dev_card, text="Iliass Wakkar", font=("Segoe UI Bold", 17), fg="#FFFFFF", bg="#0F172A").pack(anchor=tk.W, pady=(2, 0))
        tk.Label(dev_card, text="SAP Technical Engineer (ABAP Specialist) • Full-Stack Developer", font=("Segoe UI Semibold", 10), fg="#38BDF8", bg="#0F172A").pack(anchor=tk.W, pady=(2, 6))

        desc_text = "Specializing in SAP ABAP, S/4HANA, BTP, Fiori/UI5, CAP and modern Full-Stack web engineering (Next.js, Python, Spring Boot, AI integration)."
        tk.Label(dev_card, text=desc_text, font=("Segoe UI", 9), fg="#CBD5E1", bg="#0F172A", wraplength=660, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 10))

        badge = tk.Label(dev_card, text="🌐 100% Free & Open Source for Public Use", font=("Segoe UI", 9, "bold"), fg="#4ADE80", bg="#1E293B", padx=8, pady=3)
        badge.pack(anchor=tk.W)

        # Connect Links Card
        links_card = ttk.LabelFrame(container, text=" 📬 Connect & Resources ", style="Card.TLabelframe", padding=14)
        links_card.pack(fill=tk.BOTH, expand=True)

        links = [
            ("⭐ GitHub Repository (MdDoc-Studio)", "https://github.com/iliass-wakkar/MdDoc-Studio", "#1E3A5F"),
            ("🌐 Personal Website (www.wakkar.net)", "https://www.wakkar.net", "#2E8B8B"),
            ("🐙 GitHub Profile (@iliass-wakkar)", "https://github.com/iliass-wakkar", "#334155"),
            ("💼 LinkedIn Profile (@iliass-wakkar)", "https://linkedin.com/in/iliass-wakkar", "#0077B5"),
            ("✉️ Email: iliasswakkar.wip@gmail.com", "mailto:iliasswakkar.wip@gmail.com", "#475569")
        ]

        for text, url, color in links:
            f = tk.Frame(links_card, bg="#FFFFFF", pady=3)
            f.pack(fill=tk.X)
            lbl = tk.Label(f, text=text, font=("Segoe UI Semibold", 10), fg=color, bg="#FFFFFF", cursor="hand2")
            lbl.pack(side=tk.LEFT)
            lbl.bind("<Button-1>", lambda e, target=url: webbrowser.open(target))

    def _on_theme_selection(self, event=None):
        tname = self.var_theme.get()
        if tname == "custom":
            self.lbl_theme_desc.config(text="Custom Palette — User-defined colors and typography fonts.")
        else:
            tinfo = get_theme(tname)
            self.lbl_theme_desc.config(text=f"{tinfo['name']} — {tinfo['description']}")

    def _pick_color(self, which: str):
        current = getattr(self, f"custom_{which}")
        color = colorchooser.askcolor(color=current, title=f"Choose {which.title()} Color")
        if color and color[1]:
            hex_val = color[1].upper()
            setattr(self, f"custom_{which}", hex_val)
            if which == "primary":
                self.swatch_p.config(bg=hex_val)
                self.var_hex_p.set(hex_val)
            elif which == "secondary":
                self.swatch_s.config(bg=hex_val)
                self.var_hex_s.set(hex_val)
            elif which == "accent":
                self.swatch_a.config(bg=hex_val)
                self.var_hex_a.set(hex_val)
            self.var_theme.set("custom")
            self._on_theme_selection()

    def _apply_preset(self, preset_name: str):
        presets = {
            "violet": ("#7C3AED", "#EC4899", "#F59E0B", "Georgia", "Calibri"),
            "sunset": ("#EA580C", "#DB2777", "#F59E0B", "Trebuchet MS", "Segoe UI"),
            "emerald": ("#059669", "#0D9488", "#EAB308", "Cambria", "Calibri"),
            "amber": ("#B45309", "#D97706", "#E11D48", "Georgia", "Georgia")
        }
        if preset_name in presets:
            p, s, a, fh, fb = presets[preset_name]
            self.custom_primary, self.custom_secondary, self.custom_accent = p, s, a
            self.swatch_p.config(bg=p)
            self.var_hex_p.set(p)
            self.swatch_s.config(bg=s)
            self.var_hex_s.set(s)
            self.swatch_a.config(bg=a)
            self.var_hex_a.set(a)
            self.var_font_head.set(fh)
            self.var_font_body.set(fb)
            self.var_theme.set("custom")
            self._on_theme_selection()

    def _load_sample(self):
        self.txt_editor.delete("1.0", tk.END)
        self.txt_editor.insert(tk.END, SAMPLE_MD_TEXT)
        self.var_title.set("MdDoc Architecture & Specification")
        self.var_subtitle.set("High-Performance Markdown to Publication-Quality Word DOCX")
        self.var_author.set("Engineering Team")
        self.var_date.set("August 2026")
        self.var_theme.set("modern")
        self._on_theme_selection()
        messagebox.showinfo("Sample Loaded", "Sample markdown document loaded into editor!")

    def _clear_content(self):
        if messagebox.askyesno("Clear Editor", "Are you sure you want to clear the editor content?"):
            self.txt_editor.delete("1.0", tk.END)
            self.var_title.set("")
            self.var_subtitle.set("")
            self.var_author.set("")
            self.var_date.set("")

    def _browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Markdown File",
            filetypes=[("Markdown Files", "*.md;*.markdown;*.mdown"), ("All Files", "*.*")]
        )
        if file_path:
            self.var_input_file.set(file_path)
            base, _ = os.path.splitext(file_path)
            self.var_output_file.set(base + ".docx")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.txt_editor.delete("1.0", tk.END)
                self.txt_editor.insert(tk.END, content)

                fm, _ = parse_frontmatter(content)
                if "title" in fm: self.var_title.set(str(fm["title"]))
                if "subtitle" in fm: self.var_subtitle.set(str(fm["subtitle"]))
                if "author" in fm: self.var_author.set(str(fm["author"]))
                if "date" in fm: self.var_date.set(str(fm["date"]))
                if "theme" in fm and fm["theme"].lower() in THEMES:
                    self.var_theme.set(fm["theme"].lower())
                    self._on_theme_selection()
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

    def _launch_web_studio(self):
        webbrowser.open("http://localhost:8899")

    def _start_conversion(self):
        text = self.txt_editor.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Missing Markdown", "Please enter or select Markdown content first.")
            return

        out_path = self.var_output_file.get().strip()
        if not out_path:
            # Pick a save path
            doc_title = self.var_title.get().strip() or "document"
            clean_title = "".join(c for c in doc_title if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
            default_name = f"{clean_title or 'document'}.docx"
            out_path = filedialog.asksaveasfilename(
                title="Save Word Document",
                initialfile=default_name,
                defaultextension=".docx",
                filetypes=[("Word Document", "*.docx")]
            )
            if not out_path:
                return
            self.var_output_file.set(out_path)

        self.btn_convert.config(state="disabled")
        self.var_status.set("⏳ Generating Word Document with publication-quality formatting...")
        self.result_frame.pack_forget()

        threading.Thread(target=self._run_conversion, args=(text, out_path), daemon=True).start()

    def _run_conversion(self, md_content: str, out_path: str):
        theme_name = self.var_theme.get()
        title = self.var_title.get().strip() or None
        subtitle = self.var_subtitle.get().strip() or None
        author = self.var_author.get().strip() or None
        date = self.var_date.get().strip() or None
        show_cover = self.var_cover.get()
        show_toc = self.var_toc.get()
        page_size = self.var_pagesize.get()

        custom_dict = None
        if theme_name == "custom":
            custom_dict = create_custom_theme(
                primary=self.var_hex_p.get().strip(),
                secondary=self.var_hex_s.get().strip(),
                accent=self.var_hex_a.get().strip(),
                font_heading=self.var_font_head.get().strip(),
                font_body=self.var_font_body.get().strip()
            )

        try:
            converter = convert_markdown_to_docx(
                md_content=md_content,
                output_path=out_path,
                theme_name=theme_name,
                custom_theme=custom_dict,
                title=title,
                subtitle=subtitle,
                author=author,
                date=date,
                show_cover=show_cover,
                show_toc=show_toc,
                page_size=page_size
            )
            self.last_generated_path = out_path
            self.root.after(0, self._on_success, out_path)
        except Exception as e:
            self.root.after(0, self._on_error, str(e))

    def _on_success(self, output_file: str):
        self.btn_convert.config(state="normal")
        self.var_status.set(f"✔ Successfully generated: {os.path.basename(output_file)}")
        self.result_frame.pack(fill=tk.X, pady=(6, 0))

    def _on_error(self, err_msg: str):
        self.btn_convert.config(state="normal")
        self.var_status.set("❌ Conversion failed.")
        messagebox.showerror("Error", f"Failed to generate Word document:\n\n{err_msg}")

    def _open_in_word(self):
        if self.last_generated_path and os.path.exists(self.last_generated_path):
            os.startfile(self.last_generated_path)

    def _open_in_explorer(self):
        if self.last_generated_path and os.path.exists(self.last_generated_path):
            subprocess.run(f'explorer /select,"{os.path.abspath(self.last_generated_path)}"', shell=True)


def launch_gui():
    root = tk.Tk()
    app = MdDocGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
