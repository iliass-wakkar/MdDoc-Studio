"""
Modern Desktop GUI for MdDoc Studio.
Built with CustomTkinter for a sleek, modern Windows 11 / macOS interface.
Supports dynamic Creamy Light Blue & Deep Obsidian Dark themes with automatic transitions.
Fixed non-resizable pixel-perfect layout with sidebar navigation, live editor, custom theme designer, and developer profile.
"""

import os
import sys
import threading
import subprocess
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser

# High-DPI scaling on Windows
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import customtkinter as ctk

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from .themes import THEMES, get_theme, create_custom_theme
    from .native_converter import parse_frontmatter, convert_markdown_to_docx
except (ImportError, ValueError):
    from mddoc.themes import THEMES, get_theme, create_custom_theme
    from mddoc.native_converter import parse_frontmatter, convert_markdown_to_docx


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

**MdDoc Studio** is a standalone, 100% offline desktop application designed to convert Markdown into publication-quality Microsoft Word documents (`.docx`).

> "Good typography makes documents effortless to read and impactful to deliver."

---

# Key Features

| Feature | Capability | Status |
|---|---|---|
| **Curated & Custom Themes** | Modern, Nordic, Academic, Forest, Corporate, Custom | Active |
| **Cover Page Generator** | Clean typography & geometric accents | Included |
| **Table Formatting** | Booktabs style with zebra striping | Enabled |
| **GFM Admonitions** | Note, Tip, Warning & Caution callouts | Supported |

## Callout Alerts

> [!NOTE]
> This document was generated using MdDoc Studio Desktop Engine.

> [!TIP]
> Customize fonts and colors in the "Themes & Colors" tab!
"""


class MdDocModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Window Configuration (Fixed Non-Resizable Layout)
        self.title("MdDoc Studio — Markdown to Word DOCX")
        self.geometry("900x780")
        self.resizable(False, False)

        # Center window on screen
        self._center_window(900, 780)

        # Creamy Ice-Blue in Light Mode / Deep Obsidian in Dark Mode
        self.configure(fg_color=("#F0F4F8", "#0B0F19"))
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Custom Palette State
        self.custom_primary = "#2563EB"
        self.custom_secondary = "#0EA5E9"
        self.custom_accent = "#F59E0B"
        self.last_generated_path = None

        self._set_window_icon()
        self._create_layout()

    def _center_window(self, width: int, height: int):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = max(20, (screen_height - height) // 2 - 30)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _set_window_icon(self):
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        possible_paths = [
            os.path.join(base_dir, "assets", "icon.ico"),
            os.path.join(base_dir, "icon.ico"),
            os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico"),
            os.path.join(os.getcwd(), "assets", "icon.ico"),
            "assets/icon.ico",
            "icon.ico"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                try:
                    self.iconbitmap(p)
                    self.after(200, lambda path=p: self.iconbitmap(path))
                    break
                except Exception:
                    pass

    def _create_layout(self):
        # Configure Grid (2 columns: Sidebar & Main Area)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 1. LEFT SIDEBAR NAVIGATION
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=("#E2E8F0", "#070B12"),
            border_color=("#CBD5E1", "#1E293B"),
            border_width=1
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        # Brand Header
        lbl_logo = ctk.CTkLabel(
            self.sidebar_frame,
            text="📄 MdDoc Studio",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=("#0F172A", "#FFFFFF")
        )
        lbl_logo.grid(row=0, column=0, padx=20, pady=(24, 4), sticky="w")

        lbl_version = ctk.CTkLabel(
            self.sidebar_frame,
            text="v1.0.0 • Desktop Edition",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#0284C7", "#38BDF8")
        )
        lbl_version.grid(row=1, column=0, padx=20, pady=(0, 24), sticky="w")

        # Nav Buttons
        self.btn_nav_doc = ctk.CTkButton(
            self.sidebar_frame,
            text="  📝  Document & Editor",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            anchor="w",
            height=38,
            corner_radius=8,
            fg_color=("#2563EB", "#2563EB"),
            hover_color=("#1D4ED8", "#1D4ED8"),
            text_color=("#FFFFFF", "#FFFFFF"),
            command=lambda: self._select_view("doc")
        )
        self.btn_nav_doc.grid(row=2, column=0, padx=14, pady=4, sticky="ew")

        self.btn_nav_theme = ctk.CTkButton(
            self.sidebar_frame,
            text="  🎨  Themes & Colors",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            anchor="w",
            height=38,
            corner_radius=8,
            fg_color="transparent",
            hover_color=("#CBD5E1", "#1E293B"),
            text_color=("#334155", "#94A3B8"),
            command=lambda: self._select_view("theme")
        )
        self.btn_nav_theme.grid(row=3, column=0, padx=14, pady=4, sticky="ew")

        self.btn_nav_about = ctk.CTkButton(
            self.sidebar_frame,
            text="  👨‍💻  Developer & About",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            anchor="w",
            height=38,
            corner_radius=8,
            fg_color="transparent",
            hover_color=("#CBD5E1", "#1E293B"),
            text_color=("#334155", "#94A3B8"),
            command=lambda: self._select_view("about")
        )
        self.btn_nav_about.grid(row=4, column=0, padx=14, pady=4, sticky="ew")

        # Open Web Studio Button
        btn_open_web = ctk.CTkButton(
            self.sidebar_frame,
            text="🌐 Launch Web Studio",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=("#0284C7", "#0284C7"),
            hover_color=("#0369A1", "#0369A1"),
            text_color=("#FFFFFF", "#FFFFFF"),
            height=34,
            corner_radius=8,
            command=self._launch_web_studio
        )
        btn_open_web.grid(row=5, column=0, padx=14, pady=(16, 4), sticky="ew")

        # Appearance Mode Selector at bottom of sidebar
        lbl_mode = ctk.CTkLabel(
            self.sidebar_frame,
            text="Theme Mode:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#475569", "#64748B")
        )
        lbl_mode.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")

        self.opt_mode = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Dark", "Light", "System"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=("#FFFFFF", "#1E293B"),
            button_color=("#CBD5E1", "#334155"),
            button_hover_color=("#94A3B8", "#475569"),
            text_color=("#0F172A", "#FFFFFF"),
            height=28,
            command=ctk.set_appearance_mode
        )
        self.opt_mode.grid(row=8, column=0, padx=14, pady=(4, 20), sticky="ew")

        # ==========================================
        # 2. MAIN RIGHT CONTENT CONTAINER
        # ==========================================
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=16)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Views
        self.view_doc = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.view_theme = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.view_about = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")

        self._build_doc_view()
        self._build_theme_view()
        self._build_about_view()

        # Show Document view by default
        self._select_view("doc")

    def _select_view(self, name: str):
        # Update Nav Active Colors
        self.btn_nav_doc.configure(
            fg_color="#2563EB" if name == "doc" else "transparent",
            text_color=("#FFFFFF", "#FFFFFF") if name == "doc" else ("#334155", "#94A3B8")
        )
        self.btn_nav_theme.configure(
            fg_color="#2563EB" if name == "theme" else "transparent",
            text_color=("#FFFFFF", "#FFFFFF") if name == "theme" else ("#334155", "#94A3B8")
        )
        self.btn_nav_about.configure(
            fg_color="#2563EB" if name == "about" else "transparent",
            text_color=("#FFFFFF", "#FFFFFF") if name == "about" else ("#334155", "#94A3B8")
        )

        self.view_doc.grid_forget()
        self.view_theme.grid_forget()
        self.view_about.grid_forget()

        if name == "doc":
            self.view_doc.grid(row=0, column=0, sticky="nsew")
        elif name == "theme":
            self.view_theme.grid(row=0, column=0, sticky="nsew")
        elif name == "about":
            self.view_about.grid(row=0, column=0, sticky="nsew")

    # ==========================================
    # VIEW 1: DOCUMENT & EDITOR
    # ==========================================
    def _build_doc_view(self):
        # Header Toolbar Card
        top_bar = ctk.CTkFrame(
            self.view_doc,
            corner_radius=10,
            fg_color=("#FFFFFF", "#131C2E"),
            border_color=("#CBD5E1", "#1E293B"),
            border_width=1
        )
        top_bar.pack(fill="x", pady=(0, 10))

        lbl_file = ctk.CTkLabel(
            top_bar,
            text="Markdown:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#0F172A", "#FFFFFF")
        )
        lbl_file.pack(side="left", padx=(14, 8), pady=10)

        self.var_input_file = tk.StringVar()
        self.entry_input = ctk.CTkEntry(
            top_bar,
            textvariable=self.var_input_file,
            placeholder_text="Select a .md file or write directly below...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=("#F8FAFC", "#0A0F1A"),
            border_color=("#CBD5E1", "#334155"),
            text_color=("#0F172A", "#F8FAFC"),
            height=32
        )
        self.entry_input.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=10)

        btn_browse = ctk.CTkButton(
            top_bar,
            text="📂 Open",
            width=70,
            height=32,
            fg_color=("#2563EB", "#2563EB"),
            hover_color=("#1D4ED8", "#1D4ED8"),
            text_color=("#FFFFFF", "#FFFFFF"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._browse_input_file
        )
        btn_browse.pack(side="left", padx=(0, 6), pady=10)

        btn_sample = ctk.CTkButton(
            top_bar,
            text="📋 Sample",
            width=75,
            height=32,
            fg_color=("#E2E8F0", "#1E293B"),
            hover_color=("#CBD5E1", "#334155"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self._load_sample
        )
        btn_sample.pack(side="left", padx=(0, 6), pady=10)

        btn_clear = ctk.CTkButton(
            top_bar,
            text="🗑️ Clear",
            width=65,
            height=32,
            fg_color=("#E2E8F0", "#334155"),
            hover_color=("#CBD5E1", "#475569"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self._clear_content
        )
        btn_clear.pack(side="left", padx=(0, 14), pady=10)

        # Markdown Editor Box
        self.txt_editor = ctk.CTkTextbox(
            self.view_doc,
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=10,
            fg_color=("#FFFFFF", "#0A0F1A"),
            border_color=("#CBD5E1", "#1E293B"),
            border_width=1,
            text_color=("#0F172A", "#F8FAFC"),
            height=280
        )
        self.txt_editor.pack(fill="both", expand=True, pady=(0, 10))
        self.txt_editor.insert("1.0", SAMPLE_MD_TEXT)

        # Document Options & Metadata Card
        opts_card = ctk.CTkFrame(
            self.view_doc,
            corner_radius=10,
            fg_color=("#FFFFFF", "#131C2E"),
            border_color=("#CBD5E1", "#1E293B"),
            border_width=1
        )
        opts_card.pack(fill="x", pady=(0, 10))

        # Toggles Row
        tog_row = ctk.CTkFrame(opts_card, fg_color="transparent")
        tog_row.pack(fill="x", padx=14, pady=(12, 8))

        self.var_cover = tk.BooleanVar(value=True)
        self.sw_cover = ctk.CTkSwitch(
            tog_row,
            text="Cover Page",
            variable=self.var_cover,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#0F172A", "#FFFFFF"),
            progress_color=("#2563EB", "#2563EB")
        )
        self.sw_cover.pack(side="left", padx=(0, 20))

        self.var_toc = tk.BooleanVar(value=True)
        self.sw_toc = ctk.CTkSwitch(
            tog_row,
            text="Table of Contents",
            variable=self.var_toc,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#0F172A", "#FFFFFF"),
            progress_color=("#2563EB", "#2563EB")
        )
        self.sw_toc.pack(side="left", padx=(0, 20))

        lbl_psize = ctk.CTkLabel(
            tog_row,
            text="Page Size:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("#475569", "#94A3B8")
        )
        lbl_psize.pack(side="left", padx=(10, 6))

        self.var_pagesize = tk.StringVar(value="A4")
        self.opt_pagesize = ctk.CTkOptionMenu(
            tog_row,
            values=["A4", "Letter"],
            variable=self.var_pagesize,
            fg_color=("#F1F5F9", "#0A0F1A"),
            button_color=("#2563EB", "#2563EB"),
            button_hover_color=("#1D4ED8", "#1D4ED8"),
            text_color=("#0F172A", "#FFFFFF"),
            width=90,
            height=28
        )
        self.opt_pagesize.pack(side="left")

        # Metadata Grid (Title, Author, Subtitle, Date)
        meta_grid = ctk.CTkFrame(opts_card, fg_color="transparent")
        meta_grid.pack(fill="x", padx=14, pady=(0, 12))
        meta_grid.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(meta_grid, text="Title:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#475569", "#94A3B8")).grid(row=0, column=0, sticky="w", padx=(0, 6), pady=2)
        self.var_title = tk.StringVar()
        self.entry_title = ctk.CTkEntry(meta_grid, textvariable=self.var_title, placeholder_text="Document Title", fg_color=("#F8FAFC", "#0A0F1A"), border_color=("#CBD5E1", "#334155"), text_color=("#0F172A", "#F8FAFC"), height=28)
        self.entry_title.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=2)

        ctk.CTkLabel(meta_grid, text="Author:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#475569", "#94A3B8")).grid(row=0, column=2, sticky="w", padx=(0, 6), pady=2)
        self.var_author = tk.StringVar()
        self.entry_author = ctk.CTkEntry(meta_grid, textvariable=self.var_author, placeholder_text="e.g. Engineering Team", fg_color=("#F8FAFC", "#0A0F1A"), border_color=("#CBD5E1", "#334155"), text_color=("#0F172A", "#F8FAFC"), height=28)
        self.entry_author.grid(row=0, column=3, sticky="ew", pady=2)

        ctk.CTkLabel(meta_grid, text="Subtitle:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#475569", "#94A3B8")).grid(row=1, column=0, sticky="w", padx=(0, 6), pady=2)
        self.var_subtitle = tk.StringVar()
        self.entry_subtitle = ctk.CTkEntry(meta_grid, textvariable=self.var_subtitle, placeholder_text="Optional Subtitle", fg_color=("#F8FAFC", "#0A0F1A"), border_color=("#CBD5E1", "#334155"), text_color=("#0F172A", "#F8FAFC"), height=28)
        self.entry_subtitle.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=2)

        ctk.CTkLabel(meta_grid, text="Date:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#475569", "#94A3B8")).grid(row=1, column=2, sticky="w", padx=(0, 6), pady=2)
        self.var_date = tk.StringVar()
        self.entry_date = ctk.CTkEntry(meta_grid, textvariable=self.var_date, placeholder_text="Optional Date", fg_color=("#F8FAFC", "#0A0F1A"), border_color=("#CBD5E1", "#334155"), text_color=("#0F172A", "#F8FAFC"), height=28)
        self.entry_date.grid(row=1, column=3, sticky="ew", pady=2)

        # Primary Action CTA Button & Status
        action_box = ctk.CTkFrame(self.view_doc, corner_radius=10, fg_color="transparent")
        action_box.pack(fill="x", pady=(2, 0))

        self.btn_convert = ctk.CTkButton(
            action_box,
            text="⬇️  Convert & Save Word Document (.docx)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=46,
            corner_radius=8,
            fg_color=("#2563EB", "#2563EB"),
            hover_color=("#1D4ED8", "#1D4ED8"),
            text_color=("#FFFFFF", "#FFFFFF"),
            command=self._start_conversion
        )
        self.btn_convert.pack(fill="x")

        self.var_status = tk.StringVar(value="Ready. Write or open Markdown to convert.")
        self.lbl_status = ctk.CTkLabel(
            action_box,
            textvariable=self.var_status,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("#475569", "#94A3B8")
        )
        self.lbl_status.pack(anchor="w", pady=(6, 0))

        # Result Action Bar
        self.result_frame = ctk.CTkFrame(action_box, fg_color="transparent")
        self.result_frame.pack(fill="x", pady=(4, 0))

        self.btn_open_word = ctk.CTkButton(
            self.result_frame,
            text="📂 Open in Word",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=32,
            fg_color=("#10B981", "#10B981"),
            hover_color=("#059669", "#059669"),
            text_color=("#FFFFFF", "#FFFFFF"),
            command=self._open_in_word
        )
        self.btn_open_word.pack(side="left", padx=(0, 10))

        self.btn_open_dir = ctk.CTkButton(
            self.result_frame,
            text="📁 Show in File Explorer",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=32,
            fg_color=("#E2E8F0", "#334155"),
            hover_color=("#CBD5E1", "#475569"),
            text_color=("#0F172A", "#F8FAFC"),
            command=self._open_in_explorer
        )
        self.btn_open_dir.pack(side="left")

        self.result_frame.pack_forget()

    # ==========================================
    # VIEW 2: THEMES & CUSTOM COLORS
    # ==========================================
    def _build_theme_view(self):
        # 1. Curated Themes Card
        curated_card = ctk.CTkFrame(
            self.view_theme,
            corner_radius=10,
            fg_color=("#FFFFFF", "#131C2E"),
            border_color=("#CBD5E1", "#1E293B"),
            border_width=1
        )
        curated_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            curated_card,
            text="🎨 Curated Design Palettes",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=("#0F172A", "#FFFFFF")
        ).pack(anchor="w", padx=16, pady=(14, 6))

        t_row = ctk.CTkFrame(curated_card, fg_color="transparent")
        t_row.pack(fill="x", padx=16, pady=(0, 6))

        ctk.CTkLabel(
            t_row,
            text="Select Theme:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=("#475569", "#CBD5E1")
        ).pack(side="left", padx=(0, 10))

        self.var_theme = tk.StringVar(value="modern")
        self.opt_theme = ctk.CTkOptionMenu(
            t_row,
            values=["modern", "nordic", "academic", "forest", "corporate", "custom"],
            variable=self.var_theme,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=("#F1F5F9", "#0A0F1A"),
            button_color=("#2563EB", "#2563EB"),
            button_hover_color=("#1D4ED8", "#1D4ED8"),
            text_color=("#0F172A", "#FFFFFF"),
            width=200,
            command=self._on_theme_selection
        )
        self.opt_theme.pack(side="left")

        self.lbl_theme_desc = ctk.CTkLabel(
            curated_card,
            text="Modern Tech — Cambria/Calibri typography, Deep navy headings, teal accents.",
            font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"),
            text_color=("#475569", "#94A3B8")
        )
        self.lbl_theme_desc.pack(anchor="w", padx=16, pady=(0, 14))

        # 2. Custom Palette Designer Card
        custom_card = ctk.CTkFrame(
            self.view_theme,
            corner_radius=10,
            fg_color=("#FFFFFF", "#131C2E"),
            border_color=("#CBD5E1", "#1E293B"),
            border_width=1
        )
        custom_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            custom_card,
            text="✨ Custom Theme & Typography Designer",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=("#0F172A", "#FFFFFF")
        ).pack(anchor="w", padx=16, pady=(14, 10))

        # Quick Presets
        preset_row = ctk.CTkFrame(custom_card, fg_color="transparent")
        preset_row.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(
            preset_row,
            text="Quick Presets:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#475569", "#CBD5E1")
        ).pack(side="left", padx=(0, 10))

        presets = [
            ("💜 Violet", "violet", "#7C3AED"),
            ("🌅 Sunset", "sunset", "#EA580C"),
            ("🍃 Emerald", "emerald", "#059669"),
            ("☕ Amber", "amber", "#D97706")
        ]
        for label, name, col in presets:
            btn = ctk.CTkButton(
                preset_row,
                text=label,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                width=80,
                height=28,
                fg_color=col,
                hover_color="#0F172A",
                text_color="#FFFFFF",
                command=lambda p=name: self._apply_preset(p)
            )
            btn.pack(side="left", padx=4)

        # Color Pickers Container
        pickers_grid = ctk.CTkFrame(custom_card, fg_color="transparent")
        pickers_grid.pack(fill="x", padx=16, pady=(0, 14))
        pickers_grid.grid_columnconfigure((0, 1, 2), weight=1)

        # Primary
        f_p = ctk.CTkFrame(pickers_grid, corner_radius=8, fg_color=("#F8FAFC", "#0A0F1A"), border_color=("#CBD5E1", "#1E293B"), border_width=1)
        f_p.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(f_p, text="Primary Color (H1)", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#0284C7", "#38BDF8")).pack(anchor="w", padx=10, pady=(8, 4))
        self.btn_swatch_p = ctk.CTkButton(
            f_p,
            text=self.custom_primary,
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            fg_color=self.custom_primary,
            hover_color=self.custom_primary,
            text_color="#FFFFFF",
            height=34,
            command=lambda: self._pick_color('primary')
        )
        self.btn_swatch_p.pack(fill="x", padx=10, pady=(0, 10))

        # Secondary
        f_s = ctk.CTkFrame(pickers_grid, corner_radius=8, fg_color=("#F8FAFC", "#0A0F1A"), border_color=("#CBD5E1", "#1E293B"), border_width=1)
        f_s.grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkLabel(f_s, text="Secondary (Accents)", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#0284C7", "#38BDF8")).pack(anchor="w", padx=10, pady=(8, 4))
        self.btn_swatch_s = ctk.CTkButton(
            f_s,
            text=self.custom_secondary,
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            fg_color=self.custom_secondary,
            hover_color=self.custom_secondary,
            text_color="#FFFFFF",
            height=34,
            command=lambda: self._pick_color('secondary')
        )
        self.btn_swatch_s.pack(fill="x", padx=10, pady=(0, 10))

        # Accent
        f_a = ctk.CTkFrame(pickers_grid, corner_radius=8, fg_color=("#F8FAFC", "#0A0F1A"), border_color=("#CBD5E1", "#1E293B"), border_width=1)
        f_a.grid(row=0, column=2, sticky="ew", padx=(8, 0))
        ctk.CTkLabel(f_a, text="Highlight Color", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#0284C7", "#38BDF8")).pack(anchor="w", padx=10, pady=(8, 4))
        self.btn_swatch_a = ctk.CTkButton(
            f_a,
            text=self.custom_accent,
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            fg_color=self.custom_accent,
            hover_color=self.custom_accent,
            text_color="#FFFFFF",
            height=34,
            command=lambda: self._pick_color('accent')
        )
        self.btn_swatch_a.pack(fill="x", padx=10, pady=(0, 10))

        # Typography Font Selectors
        font_box = ctk.CTkFrame(custom_card, fg_color="transparent")
        font_box.pack(fill="x", padx=16, pady=(0, 16))
        font_box.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(font_box, text="Heading Font:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=("#0F172A", "#CBD5E1")).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)
        self.var_font_head = tk.StringVar(value="Georgia")
        self.opt_font_head = ctk.CTkOptionMenu(
            font_box,
            values=["Georgia", "Cambria", "Segoe UI", "Arial", "Garamond", "Trebuchet MS", "Times New Roman"],
            variable=self.var_font_head,
            fg_color=("#F1F5F9", "#0A0F1A"),
            button_color=("#2563EB", "#2563EB"),
            button_hover_color=("#1D4ED8", "#1D4ED8"),
            text_color=("#0F172A", "#FFFFFF"),
            height=30
        )
        self.opt_font_head.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=6)

        ctk.CTkLabel(font_box, text="Body Font:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=("#0F172A", "#CBD5E1")).grid(row=0, column=2, sticky="w", padx=(0, 8), pady=6)
        self.var_font_body = tk.StringVar(value="Calibri")
        self.opt_font_body = ctk.CTkOptionMenu(
            font_box,
            values=["Calibri", "Segoe UI", "Georgia", "Arial", "Garamond", "Times New Roman"],
            variable=self.var_font_body,
            fg_color=("#F1F5F9", "#0A0F1A"),
            button_color=("#2563EB", "#2563EB"),
            button_hover_color=("#1D4ED8", "#1D4ED8"),
            text_color=("#0F172A", "#FFFFFF"),
            height=30
        )
        self.opt_font_body.grid(row=0, column=3, sticky="ew", pady=6)

    # ==========================================
    # VIEW 3: DEVELOPER & ABOUT
    # ==========================================
    def _build_about_view(self):
        # Developer Card
        dev_card = ctk.CTkFrame(
            self.view_about,
            corner_radius=12,
            fg_color=("#FFFFFF", "#070B12"),
            border_color=("#CBD5E1", "#1E293B"),
            border_width=1
        )
        dev_card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            dev_card,
            text="👨‍💻 Developed By",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#0284C7", "#38BDF8")
        ).pack(anchor="w", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            dev_card,
            text="Iliass Wakkar",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=("#0F172A", "#FFFFFF")
        ).pack(anchor="w", padx=20)

        ctk.CTkLabel(
            dev_card,
            text="SAP Technical Engineer (ABAP Specialist) • Full-Stack Developer",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#0284C7", "#38BDF8")
        ).pack(anchor="w", padx=20, pady=(2, 8))

        desc = (
            "Specialized in SAP ABAP, S/4HANA, BTP, Fiori/UI5, CAP and modern Full-Stack "
            "web engineering (Next.js, Python, Spring Boot, AI integration)."
        )
        ctk.CTkLabel(
            dev_card,
            text=desc,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("#334155", "#CBD5E1"),
            wraplength=600,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 12))

        # Public service badge
        badge = ctk.CTkLabel(
            dev_card,
            text="🌐 100% Free & Open Source for Public Use",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#16A34A", "#4ADE80"),
            fg_color=("#DCFCE7", "#1E293B"),
            corner_radius=6,
            padx=10,
            pady=4
        )
        badge.pack(anchor="w", padx=20, pady=(0, 16))

        # Connect Links Card
        links_card = ctk.CTkFrame(
            self.view_about,
            corner_radius=12,
            fg_color=("#FFFFFF", "#131C2E"),
            border_color=("#CBD5E1", "#1E293B"),
            border_width=1
        )
        links_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            links_card,
            text="📬 Connect & Resources",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=("#0F172A", "#FFFFFF")
        ).pack(anchor="w", padx=16, pady=(16, 12))

        links = [
            ("⭐ GitHub Repository (MdDoc-Studio)", "https://github.com/iliass-wakkar/MdDoc-Studio", "#2563EB"),
            ("🌐 Personal Website (www.wakkar.net)", "https://www.wakkar.net", "#0284C7"),
            ("🐙 GitHub Profile (@iliass-wakkar)", "https://github.com/iliass-wakkar", "#334155"),
            ("💼 LinkedIn Profile (@iliass-wakkar)", "https://linkedin.com/in/iliass-wakkar", "#0077B5"),
            ("✉️ Contact Email (iliasswakkar.wip@gmail.com)", "mailto:iliasswakkar.wip@gmail.com", "#475569")
        ]

        for text, url, col in links:
            btn = ctk.CTkButton(
                links_card,
                text=f"  {text}",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                anchor="w",
                height=36,
                corner_radius=8,
                fg_color=col,
                hover_color="#0F172A",
                text_color="#FFFFFF",
                command=lambda target=url: webbrowser.open(target)
            )
            btn.pack(fill="x", padx=16, pady=4)

    # ==========================================
    # LOGIC & HANDLERS
    # ==========================================
    def _on_theme_selection(self, choice: str):
        if choice == "custom":
            self.lbl_theme_desc.configure(text="Custom Palette — User-defined colors and typography fonts.")
        else:
            tinfo = get_theme(choice)
            self.lbl_theme_desc.configure(text=f"{tinfo['name']} — {tinfo['description']}")

    def _pick_color(self, which: str):
        current = getattr(self, f"custom_{which}")
        color = colorchooser.askcolor(color=current, title=f"Choose {which.title()} Color")
        if color and color[1]:
            hex_val = color[1].upper()
            setattr(self, f"custom_{which}", hex_val)
            if which == "primary":
                self.btn_swatch_p.configure(text=hex_val, fg_color=hex_val, hover_color=hex_val)
            elif which == "secondary":
                self.btn_swatch_s.configure(text=hex_val, fg_color=hex_val, hover_color=hex_val)
            elif which == "accent":
                self.btn_swatch_a.configure(text=hex_val, fg_color=hex_val, hover_color=hex_val)
            self.var_theme.set("custom")
            self._on_theme_selection("custom")

    def _apply_preset(self, preset_name: str):
        presets = {
            "violet": ("#7C3AED", "#EC4899", "#F59E0B", "Georgia", "Calibri"),
            "sunset": ("#EA580C", "#DB2777", "#F59E0B", "Trebuchet MS", "Segoe UI"),
            "emerald": ("#059669", "#0D9488", "#EAB308", "Cambria", "Calibri"),
            "amber": ("#D97706", "#F59E0B", "#DC2626", "Georgia", "Georgia")
        }
        if preset_name in presets:
            p, s, a, fh, fb = presets[preset_name]
            self.custom_primary, self.custom_secondary, self.custom_accent = p, s, a
            self.btn_swatch_p.configure(text=p, fg_color=p, hover_color=p)
            self.btn_swatch_s.configure(text=s, fg_color=s, hover_color=s)
            self.btn_swatch_a.configure(text=a, fg_color=a, hover_color=a)
            self.var_font_head.set(fh)
            self.var_font_body.set(fb)
            self.var_theme.set("custom")
            self._on_theme_selection("custom")

    def _load_sample(self):
        self.txt_editor.delete("1.0", tk.END)
        self.txt_editor.insert("1.0", SAMPLE_MD_TEXT)
        self.var_title.set("MdDoc Architecture & Specification")
        self.var_subtitle.set("High-Performance Markdown to Publication-Quality Word DOCX")
        self.var_author.set("Engineering Team")
        self.var_date.set("August 2026")
        self.var_theme.set("modern")
        self._on_theme_selection("modern")
        messagebox.showinfo("Sample Loaded", "Sample markdown document loaded into editor!")

    def _clear_content(self):
        if messagebox.askyesno("Clear Editor", "Are you sure you want to clear all editor content?"):
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
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.txt_editor.delete("1.0", tk.END)
                self.txt_editor.insert("1.0", content)

                fm, _ = parse_frontmatter(content)
                if "title" in fm: self.var_title.set(str(fm["title"]))
                if "subtitle" in fm: self.var_subtitle.set(str(fm["subtitle"]))
                if "author" in fm: self.var_author.set(str(fm["author"]))
                if "date" in fm: self.var_date.set(str(fm["date"]))
                if "theme" in fm and fm["theme"].lower() in THEMES:
                    self.var_theme.set(fm["theme"].lower())
                    self._on_theme_selection(fm["theme"].lower())
            except Exception:
                pass

    def _launch_web_studio(self):
        webbrowser.open("http://localhost:8899")

    def _start_conversion(self):
        text = self.txt_editor.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Missing Markdown", "Please enter or select Markdown content first.")
            return

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

        self.btn_convert.configure(state="disabled", text="⏳ Generating DOCX...")
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
                primary=self.custom_primary,
                secondary=self.custom_secondary,
                accent=self.custom_accent,
                font_heading=self.var_font_head.get().strip(),
                font_body=self.var_font_body.get().strip()
            )

        try:
            convert_markdown_to_docx(
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
            self.after(0, self._on_success, out_path)
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _on_success(self, output_file: str):
        self.btn_convert.configure(state="normal", text="⬇️  Convert & Save Word Document (.docx)")
        self.var_status.set(f"✔ Successfully saved: {os.path.basename(output_file)}")
        self.result_frame.pack(fill="x", pady=(4, 0))

    def _on_error(self, err_msg: str):
        self.btn_convert.configure(state="normal", text="⬇️  Convert & Save Word Document (.docx)")
        self.var_status.set("❌ Conversion failed.")
        messagebox.showerror("Error", f"Failed to generate Word document:\n\n{err_msg}")

    def _open_in_word(self):
        if self.last_generated_path and os.path.exists(self.last_generated_path):
            os.startfile(self.last_generated_path)

    def _open_in_explorer(self):
        if self.last_generated_path and os.path.exists(self.last_generated_path):
            subprocess.run(f'explorer /select,"{os.path.abspath(self.last_generated_path)}"', shell=True)


def launch_gui():
    app = MdDocModernApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
