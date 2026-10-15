/**
 * MdDoc Studio Application JavaScript.
 * Coordinates UI, Live Preview, and WebAssembly Worker with Custom Theme support.
 */

// Default Sample Markdown
const SAMPLE_MARKDOWN = `---
title: "MdDoc Architecture & Specification"
subtitle: "High-Performance Markdown to Publication-Quality Word DOCX"
author: "Engineering Team"
date: "August 2026"
theme: "modern"
toc: true
cover_page: true
---

# Executive Summary

**MdDoc** is a 100% offline, client-side toolkit designed to convert standard Markdown into beautifully formatted, publication-ready Microsoft Word documents (\`.docx\`).

> "Good typography makes documents effortless to read and impactful to deliver."

---

# Key Features

The engine applies strict visual design principles across fonts, colors, and layout:

| Feature | Capability | Status |
|---|---|---|
| **Client-Side WASM** | Runs 100% in your browser | Active |
| **5 Curated Themes + Custom** | Modern, Nordic, Academic, Forest, Corporate, Custom | Included |
| **Cover Page Generator** | Clean typography & accent geometry | Enabled |
| **Table Formatting** | Booktabs style with zebra striping | Enabled |
| **GFM Admonitions** | Styled note & warning callout boxes | Supported |

## Callout Alerts

> [!NOTE]
> This document was generated entirely in-browser using WebAssembly.

> [!TIP]
> You can now pick your own custom colors, accents, and typography in the Custom Theme Designer!
`;

// Presets for Custom Theme
const CUSTOM_PRESETS = {
    violet: { primary: "#7C3AED", secondary: "#EC4899", accent: "#F59E0B", fontHeading: "Georgia", fontBody: "Calibri" },
    sunset: { primary: "#EA580C", secondary: "#DB2777", accent: "#F59E0B", fontHeading: "Trebuchet MS", fontBody: "Segoe UI" },
    emerald: { primary: "#059669", secondary: "#0D9488", accent: "#EAB308", fontHeading: "Cambria", fontBody: "Calibri" },
    amber: { primary: "#B45309", secondary: "#D97706", accent: "#E11D48", fontHeading: "Georgia", fontBody: "Georgia" }
};

// Application State
let selectedTheme = "modern";
let isEngineReady = false;
let worker = null;
const DRAFT_STORAGE_KEY = "mddoc-studio-draft-v1";
let draftSaveTimer = null;

// DOM Elements
const mdInput = document.getElementById('markdown-input');
const previewContent = document.getElementById('preview-content');
const tabEditorBtn = document.getElementById('tab-editor-btn');
const tabPreviewBtn = document.getElementById('tab-preview-btn');
const editorTabView = document.getElementById('editor-tab-view');
const previewTabView = document.getElementById('preview-tab-view');
const dropBanner = document.getElementById('drop-banner');
const fileInput = document.getElementById('file-input');
const btnSample = document.getElementById('btn-sample');
const btnClear = document.getElementById('btn-clear');
const btnExport = document.getElementById('btn-export');
const btnHeaderExport = document.getElementById('btn-header-export');
const btnToolbarExport = document.getElementById('btn-toolbar-export');
const btnText = document.getElementById('btn-text');
const engineStatus = document.getElementById('engine-status');
const statusText = document.getElementById('status-text');
const statusToast = document.getElementById('status-toast');
const downloadBox = document.getElementById('download-box');

// Metadata Inputs
const inpTitle = document.getElementById('meta-title');
const inpAuthor = document.getElementById('meta-author');
const inpSubtitle = document.getElementById('meta-subtitle');
const chkCover = document.getElementById('chk-cover');
const chkToc = document.getElementById('chk-toc');
const chkHeader = document.getElementById('chk-header');
const selPageSize = document.getElementById('sel-pagesize');
const btnExportTypst = document.getElementById('btn-export-typst');
const btnTypstText = document.getElementById('btn-typst-text');

// Custom Theme Controls
const customThemePanel = document.getElementById('custom-theme-panel');
const pickerPrimary = document.getElementById('picker-primary');
const pickerSecondary = document.getElementById('picker-secondary');
const pickerAccent = document.getElementById('picker-accent');
const hexPrimary = document.getElementById('hex-primary');
const hexSecondary = document.getElementById('hex-secondary');
const hexAccent = document.getElementById('hex-accent');
const selFontHeading = document.getElementById('sel-font-heading');
const selFontBody = document.getElementById('sel-font-body');
const swatchCustomP = document.getElementById('swatch-custom-p');
const swatchCustomS = document.getElementById('swatch-custom-s');
const swatchCustomA = document.getElementById('swatch-custom-a');
const customFontsLabel = document.getElementById('custom-fonts-label');

// Initialize Worker
function initWorker() {
    worker = new Worker('worker.js?v=' + Date.now());

    worker.onmessage = function (e) {
        const { type, message, data } = e.data;

        if (type === "STATUS") {
            if (statusText) statusText.innerText = message;
        } else if (type === "READY") {
            isEngineReady = true;
            window.isEngineReady = true;
            if (engineStatus) {
                engineStatus.classList.remove('loading');
                engineStatus.classList.add('ready');
            }
            if (statusText) statusText.innerText = "Engine Ready";
            if (btnExport) btnExport.disabled = false;
            if (btnHeaderExport) btnHeaderExport.disabled = false;
        } else if (type === "CONVERT_SUCCESS") {
            onExportSuccess(data);
        } else if (type === "TYPST_SUCCESS") {
            onTypstSuccess(data);
        } else if (type === "ERROR") {
            onExportError(message);
        }
    };

    worker.onerror = function (err) {
        console.error("Worker Error:", err);
        if (statusText) statusText.innerText = "Engine Error";
        showToast("Engine error: " + err.message, "error");
    };
}

// Built-in Theme Styles Specification for Live Preview
const THEME_STYLES = {
    modern: {
        fontHeading: "Cambria, Georgia, serif",
        fontBody: "Calibri, -apple-system, sans-serif",
        h1: "#1E3A5F",
        h2: "#2E5A7E",
        h3: "#4A7C94",
        secondary: "#2E8B8B",
        text: "#2D3748",
        quoteBorder: "#2E8B8B",
        quoteBg: "#F0FDF4",
        quoteText: "#334155",
        tableHeaderBg: "#1E3A5F",
        tableHeaderText: "#FFFFFF",
        tableBorder: "#CBD5E1",
        tableRowAlt: "#F8FAFC",
        codeBg: "#F8FAFC",
        codeBorder: "#CBD5E1",
        link: "#0284C7"
    },
    nordic: {
        fontHeading: "'Segoe UI Semibold', 'Segoe UI', sans-serif",
        fontBody: "'Segoe UI', -apple-system, sans-serif",
        h1: "#2E3440",
        h2: "#3B4252",
        h3: "#434C5E",
        secondary: "#5E81AC",
        text: "#3B4252",
        quoteBorder: "#5E81AC",
        quoteBg: "#F4F6F9",
        quoteText: "#2E3440",
        tableHeaderBg: "#2E3440",
        tableHeaderText: "#ECEFF4",
        tableBorder: "#D8DEE9",
        tableRowAlt: "#F4F6F9",
        codeBg: "#ECEFF4",
        codeBorder: "#D8DEE9",
        link: "#5E81AC"
    },
    academic: {
        fontHeading: "Georgia, serif",
        fontBody: "Georgia, serif",
        h1: "#1A365D",
        h2: "#2C5282",
        h3: "#2B6CB0",
        secondary: "#744210",
        text: "#1A202C",
        quoteBorder: "#744210",
        quoteBg: "#FFFAF0",
        quoteText: "#2D3748",
        tableHeaderBg: "#1A365D",
        tableHeaderText: "#FFFFFF",
        tableBorder: "#CBD5E0",
        tableRowAlt: "#F7FAFC",
        codeBg: "#FFFAF0",
        codeBorder: "#E2E8F0",
        link: "#2B6CB0"
    },
    forest: {
        fontHeading: "Cambria, Georgia, serif",
        fontBody: "Calibri, -apple-system, sans-serif",
        h1: "#1C4532",
        h2: "#276749",
        h3: "#2F855A",
        secondary: "#2F855A",
        text: "#1A202C",
        quoteBorder: "#2F855A",
        quoteBg: "#F0FFF4",
        quoteText: "#22543D",
        tableHeaderBg: "#1C4532",
        tableHeaderText: "#FFFFFF",
        tableBorder: "#C6F6D5",
        tableRowAlt: "#F7FAFC",
        codeBg: "#F0FFF4",
        codeBorder: "#C6F6D5",
        link: "#276749"
    },
    corporate: {
        fontHeading: "Arial, sans-serif",
        fontBody: "Arial, sans-serif",
        h1: "#0F2942",
        h2: "#184E77",
        h3: "#1E6091",
        secondary: "#1E6091",
        text: "#1F2937",
        quoteBorder: "#1E6091",
        quoteBg: "#F0F7FF",
        quoteText: "#1F2937",
        tableHeaderBg: "#0F2942",
        tableHeaderText: "#FFFFFF",
        tableBorder: "#D1D5DB",
        tableRowAlt: "#F9FAFB",
        codeBg: "#F9FAFB",
        codeBorder: "#E5E7EB",
        link: "#1E6091"
    }
};

function getCustomThemeStyles() {
    const p = pickerPrimary ? pickerPrimary.value : "#7C3AED";
    const s = pickerSecondary ? pickerSecondary.value : "#EC4899";
    const a = pickerAccent ? pickerAccent.value : "#F59E0B";
    const fHead = selFontHeading ? selFontHeading.value : "Georgia";
    const fBody = selFontBody ? selFontBody.value : "Calibri";

    return {
        fontHeading: `${fHead}, serif`,
        fontBody: `${fBody}, sans-serif`,
        h1: p,
        h2: p,
        h3: s,
        secondary: s,
        accent: a,
        text: "#2D3748",
        quoteBorder: s,
        quoteBg: "#FAF5FF",
        quoteText: "#334155",
        tableHeaderBg: p,
        tableHeaderText: "#FFFFFF",
        tableBorder: "#CBD5E1",
        tableRowAlt: "#FAF5FF",
        codeBg: "#FAF5FF",
        codeBorder: "#E9D5FF",
        link: s
    };
}

function buildCustomThemeDictForDocx() {
    const p = (pickerPrimary ? pickerPrimary.value : "#7C3AED").replace('#', '');
    const s = (pickerSecondary ? pickerSecondary.value : "#EC4899").replace('#', '');
    const a = (pickerAccent ? pickerAccent.value : "#F59E0B").replace('#', '');
    const fHead = selFontHeading ? selFontHeading.value : "Georgia";
    const fBody = selFontBody ? selFontBody.value : "Calibri";

    return {
        name: "Custom Palette",
        description: "User customized palette",
        font_heading: fHead,
        font_body: fBody,
        font_code: "Consolas",
        primary: p,
        secondary: s,
        accent: a,
        heading1: p,
        heading2: p,
        heading3: s,
        heading4: s,
        text: "2D3748",
        light_text: "718096",
        border: "E2E8F0",
        code_bg: "FAF5FF",
        code_border: "E9D5FF",
        code_text: "0F172A",
        quote_border: s,
        quote_bg: "FAF5FF",
        quote_text: "334155",
        table_header_bg: p,
        table_header_text: "FFFFFF",
        table_border: "CBD5E1",
        table_row_alt: "FAF5FF",
        link: s,
        hr_color: "CBD5E1",
        alerts: {
            NOTE: { color: s, bg: "FDF4FF", title: "Note", icon: "ℹ" },
            TIP: { color: "10B981", bg: "F0FDF4", title: "Tip", icon: "💡" },
            IMPORTANT: { color: p, bg: "FAF5FF", title: "Important", icon: "★" },
            WARNING: { color: a, bg: "FFFBEB", title: "Warning", icon: "⚠" },
            CAUTION: { color: "EF4444", bg: "FEF2F2", title: "Caution", icon: "🛑" }
        }
    };
}

// Apply CSS Variables to Live Preview
function applyThemeToPreview(themeName) {
    const t = (themeName === "custom") ? getCustomThemeStyles() : (THEME_STYLES[themeName] || THEME_STYLES.modern);
    const p = previewContent;
    p.style.setProperty('--theme-font-heading', t.fontHeading);
    p.style.setProperty('--theme-font-body', t.fontBody);
    p.style.setProperty('--theme-h1', t.h1);
    p.style.setProperty('--theme-h2', t.h2);
    p.style.setProperty('--theme-h3', t.h3);
    p.style.setProperty('--theme-secondary', t.secondary);
    p.style.setProperty('--theme-text', t.text);
    p.style.setProperty('--theme-quote-border', t.quoteBorder);
    p.style.setProperty('--theme-quote-bg', t.quoteBg);
    p.style.setProperty('--theme-quote-text', t.quoteText);
    p.style.setProperty('--theme-table-header-bg', t.tableHeaderBg);
    p.style.setProperty('--theme-table-header-text', t.tableHeaderText);
    p.style.setProperty('--theme-table-border', t.tableBorder);
    p.style.setProperty('--theme-table-row-alt', t.tableRowAlt);
    p.style.setProperty('--theme-code-bg', t.codeBg);
    p.style.setProperty('--theme-code-border', t.codeBorder);
    p.style.setProperty('--theme-link', t.link);
}

// Live Markdown Preview Update
function updatePreview() {
    const raw = mdInput.value;
    const cleanMd = raw.replace(/^---\s*[\r\n]+[\s\S]*?[\r\n]+---\s*[\r\n]+/, '');

    let html = "";

    if (chkCover.checked) {
        const titleText = inpTitle.value.trim() || "Document Title";
        const subText = inpSubtitle.value.trim();
        const authText = inpAuthor.value.trim();

        html += `
        <div class="preview-cover-banner">
            <div class="cover-accent-line">━━━━━━━━━━━━━━━</div>
            <div class="cover-title">${escapeHtml(titleText)}</div>
            ${subText ? `<div class="cover-subtitle">${escapeHtml(subText)}</div>` : ''}
            <div class="cover-accent-line" style="font-size:10px;">─────────────────────</div>
            ${authText ? `<div class="cover-meta">By ${escapeHtml(authText)}</div>` : ''}
            <div class="cover-accent-line">━━━━━━━━━━━━━━━</div>
        </div>
        `;
    }

    if (window.marked) {
        html += marked.parse(cleanMd);
    }

    if (window.DOMPurify) html = DOMPurify.sanitize(html, { ADD_ATTR: ['style'] });
    previewContent.innerHTML = html;
    applyThemeToPreview(selectedTheme);
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function openPrintView(title, contentHtml, pageSize = 'A4') {
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
        showToast('Allow pop-ups for this site to open the print view.', 'error');
        return false;
    }

    const safeTitle = escapeHtml(title || 'Document');
    const safePageSize = pageSize === 'Letter' ? 'Letter' : 'A4';
    const theme = selectedTheme === 'custom' ? getCustomThemeStyles() : (THEME_STYLES[selectedTheme] || THEME_STYLES.modern);
    const cssColor = (color, fallback) => /^#[0-9a-f]{6}$/i.test(color || '') ? color : fallback;
    const cssFont = (font, fallback) => (font || fallback).replace(/[^a-zA-Z0-9,' _-]/g, '');
    const printTheme = {
        body: cssColor(theme.text, '#243443'),
        heading: cssColor(theme.h1, '#183b56'),
        accent: cssColor(theme.secondary, '#147d79'),
        tableHeader: cssColor(theme.tableHeaderBg, '#183b56'),
        headingFont: cssFont(theme.fontHeading, 'Cambria, Georgia, serif'),
        bodyFont: cssFont(theme.fontBody, 'Calibri, Segoe UI, Arial, sans-serif')
    };
    const printHtml = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${safeTitle}</title>
<style>
@page { size: ${safePageSize}; margin: 18mm; }
* { box-sizing: border-box; }
body { max-width: 820px; margin: 0 auto; color: ${printTheme.body}; font: 11pt/1.65 ${printTheme.bodyFont}; }
h1,h2,h3,h4,h5,h6 { color: ${printTheme.heading}; font-family: ${printTheme.headingFont}; line-height: 1.25; margin: 1.35em 0 .5em; break-after: avoid; }
h1 { font-size: 26pt; margin-top: 0; } h2 { font-size: 19pt; border-bottom: 1px solid #d8e1e6; padding-bottom: .2em; }
p,ul,ol,blockquote,pre,table { margin: .8em 0; }
a { color: ${printTheme.accent}; text-decoration: underline; }
blockquote { border-left: 3px solid ${printTheme.accent}; margin-left: 0; padding: .2em 1em; color: #4b5d69; background: #f5f8f8; }
pre,code { font-family: Consolas, "Courier New", monospace; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f4f6f7; border: 1px solid #dfe6e9; padding: 12px; border-radius: 4px; }
code { background: #f1f4f5; padding: .12em .28em; border-radius: 3px; }
pre code { background: transparent; padding: 0; }
table { width: 100%; border-collapse: collapse; font-size: 10pt; break-inside: avoid; }
th { color: #fff; background: ${printTheme.tableHeader}; text-align: left; }
th,td { border: 1px solid #cbd6dc; padding: 7px 9px; vertical-align: top; }
tr:nth-child(even) td { background: #f6f8f9; }
img { max-width: 100%; height: auto; }
hr { border: 0; border-top: 1px solid #d8e1e6; margin: 1.5em 0; }
.print-cover { min-height: 230mm; display: flex; flex-direction: column; justify-content: center; page-break-after: always; }
.print-cover h1 { font-size: 34pt; margin: 0 0 .4em; }
.print-subtitle { font-size: 16pt; color: #627583; }
.print-byline { margin-top: 3em; color: #526574; }
@media screen { body { padding: 28px; } }
@media print { body { max-width: none; } a { color: inherit; } }
</style></head><body>${contentHtml}</body></html>`;

    let printStarted = false;
    const startPrint = () => {
        if (printStarted || printWindow.closed) return;
        printStarted = true;
        printWindow.focus();
        printWindow.print();
    };
    printWindow.addEventListener('load', startPrint, { once: true });
    printWindow.document.open();
    printWindow.document.write(printHtml);
    printWindow.document.close();
    window.setTimeout(startPrint, 400);
    return true;
}

function buildMarkdownPrintHtml(markdown) {
    const cleanMarkdown = markdown.replace(/^---\s*[\r\n]+[\s\S]*?[\r\n]+---\s*[\r\n]+/, '');
    let html = window.marked ? marked.parse(cleanMarkdown) : `<pre>${escapeHtml(cleanMarkdown)}</pre>`;
    if (window.DOMPurify) html = DOMPurify.sanitize(html);
    if (!chkCover.checked) return html;

    const title = inpTitle.value.trim() || 'Document';
    const subtitle = inpSubtitle.value.trim();
    const author = inpAuthor.value.trim();
    const cover = `<section class="print-cover"><h1>${escapeHtml(title)}</h1>${subtitle ? `<p class="print-subtitle">${escapeHtml(subtitle)}</p>` : ''}${author ? `<p class="print-byline">${escapeHtml(author)}</p>` : ''}</section>`;
    return cover + html;
}

// Frontmatter Auto-Extractor
function checkAndApplyFrontmatter(text) {
    const fmMatch = text.match(/^---\s*[\r\n]+([\s\S]*?)[\r\n]+---\s*[\r\n]+/);
    if (!fmMatch) return;

    const fmLines = fmMatch[1].split(/\r?\n/);
    fmLines.forEach(line => {
        const parts = line.split(':');
        if (parts.length >= 2) {
            const key = parts[0].trim().toLowerCase();
            const val = parts.slice(1).join(':').trim().replace(/^["']|["']$/g, '');
            if (key === "title" && !inpTitle.value) inpTitle.value = val;
            if (key === "subtitle" && !inpSubtitle.value) inpSubtitle.value = val;
            if (key === "author" && !inpAuthor.value) inpAuthor.value = val;
            if (key === "theme") selectTheme(val.toLowerCase());
            if (key === "cover_page") chkCover.checked = (val.toLowerCase() === "true");
            if (key === "toc") chkToc.checked = (val.toLowerCase() === "true");
            if (key === "header" || key === "running_header") if (chkHeader) chkHeader.checked = (val.toLowerCase() === "true");
            if (key === "page_size" && ["A4", "Letter"].includes(val)) selPageSize.value = val;
        }
    });
}

function loadMarkdownDocument(text) {
    mdInput.value = text;
    inpTitle.value = '';
    inpSubtitle.value = '';
    inpAuthor.value = '';
    chkCover.checked = false;
    chkToc.checked = false;
    chkHeader.checked = false;
    selPageSize.value = 'A4';
    selectTheme('modern');
    checkAndApplyFrontmatter(text);
    updatePreview();
    scheduleDraftSave();
}

// Theme Selector
function selectTheme(themeName) {
    const target = document.querySelector(`.theme-option[data-theme="${themeName}"]`);
    if (target) {
        document.querySelectorAll('.theme-option').forEach(el => {
            const selected = el === target;
            el.classList.toggle('active', selected);
            el.setAttribute('aria-checked', String(selected));
            el.tabIndex = selected ? 0 : -1;
        });
        target.classList.add('active');
        selectedTheme = themeName;

        // Toggle custom controls panel visibility
        if (customThemePanel) {
            customThemePanel.style.display = (themeName === "custom") ? "block" : "none";
        }

        applyThemeToPreview(themeName);
        updatePreview();
    }
}

function setDraftStatus(message) {
    const status = document.getElementById('draft-status');
    if (status) status.textContent = message;
}

function saveDraft() {
    try {
        localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify({
            markdown: mdInput.value,
            title: inpTitle.value,
            subtitle: inpSubtitle.value,
            author: inpAuthor.value,
            theme: selectedTheme,
            cover: chkCover.checked,
            toc: chkToc.checked,
            header: chkHeader.checked,
            pageSize: selPageSize.value,
            custom: {
                primary: pickerPrimary.value,
                secondary: pickerSecondary.value,
                accent: pickerAccent.value,
                headingFont: selFontHeading.value,
                bodyFont: selFontBody.value
            }
        }));
        setDraftStatus('Draft saved on this device');
    } catch (error) {
        setDraftStatus('Draft could not be saved');
    }
}

function scheduleDraftSave() {
    setDraftStatus('Saving draft…');
    clearTimeout(draftSaveTimer);
    draftSaveTimer = setTimeout(saveDraft, 400);
}

function restoreDraft() {
    try {
        const saved = localStorage.getItem(DRAFT_STORAGE_KEY);
        if (!saved) return false;
        const draft = JSON.parse(saved);
        if (!draft || typeof draft.markdown !== 'string') return false;

        mdInput.value = draft.markdown;
        inpTitle.value = draft.title || '';
        inpSubtitle.value = draft.subtitle || '';
        inpAuthor.value = draft.author || '';
        if (typeof draft.cover === 'boolean') chkCover.checked = draft.cover;
        if (typeof draft.toc === 'boolean') chkToc.checked = draft.toc;
        if (typeof draft.header === 'boolean') chkHeader.checked = draft.header;
        if (draft.pageSize === 'A4' || draft.pageSize === 'Letter') selPageSize.value = draft.pageSize;
        if (draft.custom && typeof draft.custom === 'object') {
            if (/^#[0-9a-f]{6}$/i.test(draft.custom.primary || '')) pickerPrimary.value = hexPrimary.value = draft.custom.primary;
            if (/^#[0-9a-f]{6}$/i.test(draft.custom.secondary || '')) pickerSecondary.value = hexSecondary.value = draft.custom.secondary;
            if (/^#[0-9a-f]{6}$/i.test(draft.custom.accent || '')) pickerAccent.value = hexAccent.value = draft.custom.accent;
            if (draft.custom.headingFont && [...selFontHeading.options].some(option => option.value === draft.custom.headingFont)) selFontHeading.value = draft.custom.headingFont;
            if (draft.custom.bodyFont && [...selFontBody.options].some(option => option.value === draft.custom.bodyFont)) selFontBody.value = draft.custom.bodyFont;
        }
        updateCustomSwatches();
        if (document.querySelector(`.theme-option[data-theme="${draft.theme}"]`)) selectTheme(draft.theme);
        setDraftStatus('Draft restored from this device');
        return true;
    } catch (error) {
        setDraftStatus('Draft storage unavailable');
        return false;
    }
}

function updateCustomSwatches() {
    if (swatchCustomP) swatchCustomP.style.background = pickerPrimary.value;
    if (swatchCustomS) swatchCustomS.style.background = pickerSecondary.value;
    if (swatchCustomA) swatchCustomA.style.background = pickerAccent.value;
    if (customFontsLabel) customFontsLabel.innerText = `${selFontHeading.value} • ${selFontBody.value}`;
}

function setupCustomThemeListeners() {
    // 2-way sync pickers and hex inputs
    const syncPair = (picker, hexInput) => {
        picker.addEventListener('input', () => {
            hexInput.value = picker.value.toUpperCase();
            updateCustomSwatches();
            scheduleDraftSave();
            if (selectedTheme === "custom") {
                applyThemeToPreview("custom");
                updatePreview();
            }
        });
        hexInput.addEventListener('input', () => {
            let v = hexInput.value.trim();
            if (!v.startsWith('#')) v = '#' + v;
            if (/^#[0-9A-Fa-f]{6}$/.test(v)) {
                picker.value = v;
                updateCustomSwatches();
                scheduleDraftSave();
                if (selectedTheme === "custom") {
                    applyThemeToPreview("custom");
                    updatePreview();
                }
            }
        });
    };

    if (pickerPrimary && hexPrimary) syncPair(pickerPrimary, hexPrimary);
    if (pickerSecondary && hexSecondary) syncPair(pickerSecondary, hexSecondary);
    if (pickerAccent && hexAccent) syncPair(pickerAccent, hexAccent);

    [selFontHeading, selFontBody].forEach(el => {
        if (el) {
            el.addEventListener('change', () => {
                updateCustomSwatches();
                scheduleDraftSave();
                if (selectedTheme === "custom") {
                    applyThemeToPreview("custom");
                    updatePreview();
                }
            });
        }
    });

    // Preset buttons
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const pName = btn.dataset.preset;
            const preset = CUSTOM_PRESETS[pName];
            if (preset) {
                pickerPrimary.value = preset.primary;
                hexPrimary.value = preset.primary;
                pickerSecondary.value = preset.secondary;
                hexSecondary.value = preset.secondary;
                pickerAccent.value = preset.accent;
                hexAccent.value = preset.accent;
                selFontHeading.value = preset.fontHeading;
                selFontBody.value = preset.fontBody;

                updateCustomSwatches();
                selectTheme("custom");
                scheduleDraftSave();
                showToast(`Applied "${btn.innerText}" preset!`, "success");
            }
        });
    });
}

// Tab Switching
function setupTabs() {
    const activateTab = (name, focus = false) => {
        const editorActive = name === 'editor';
        tabEditorBtn.classList.toggle('active', editorActive);
        tabPreviewBtn.classList.toggle('active', !editorActive);
        tabEditorBtn.setAttribute('aria-selected', String(editorActive));
        tabPreviewBtn.setAttribute('aria-selected', String(!editorActive));
        tabEditorBtn.tabIndex = editorActive ? 0 : -1;
        tabPreviewBtn.tabIndex = editorActive ? -1 : 0;
        editorTabView.classList.toggle('active', editorActive);
        previewTabView.classList.toggle('active', !editorActive);
        editorTabView.setAttribute('aria-hidden', String(!editorActive));
        previewTabView.setAttribute('aria-hidden', String(editorActive));
        if (!editorActive) updatePreview();
        if (focus) (editorActive ? tabEditorBtn : tabPreviewBtn).focus();
    };

    tabEditorBtn.addEventListener('click', () => activateTab('editor'));
    tabPreviewBtn.addEventListener('click', () => activateTab('preview'));
    [tabEditorBtn, tabPreviewBtn].forEach((button) => {
        button.addEventListener('keydown', (event) => {
            if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
            event.preventDefault();
            activateTab(button === tabEditorBtn ? 'preview' : 'editor', true);
        });
    });
}

function setupDropZoneAccessibility() {
    document.querySelectorAll('.drop-zone-large').forEach((zone) => {
        const fileInput = zone.querySelector('input[type="file"]');
        const title = zone.querySelector('.drop-title');
        zone.setAttribute('role', 'button');
        zone.tabIndex = 0;
        if (title) zone.setAttribute('aria-label', title.textContent.trim());
        if (fileInput) zone.setAttribute('aria-controls', fileInput.id);
        zone.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                if (fileInput) fileInput.click();
            }
        });
    });
}

// Drag and Drop & File Input
function setupFileUpload() {
    const btnOpenFile = document.getElementById('btn-open-file');
    const handleFile = (file) => {
        if (!file) return;
        if (!/\.(md|markdown|txt)$/i.test(file.name)) {
            showToast('Choose a Markdown or text file (.md, .markdown, .txt).', 'error');
            return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
            const contents = e.target.result;
            const markdown = /\.txt$/i.test(file.name)
                ? contents.split(/\r?\n/).map(line => line.trim() ? `${line}  ` : '').join('\n')
                : contents;
            loadMarkdownDocument(markdown);
            showToast(`Loaded "${file.name}"`, "success");
        };
        reader.readAsText(file);
    };

    if (btnOpenFile) btnOpenFile.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
        e.target.value = '';
    });

    window.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropBanner.classList.add('dragover');
    });

    window.addEventListener('dragleave', (e) => {
        if (e.relatedTarget === null) dropBanner.classList.remove('dragover');
    });

    window.addEventListener('drop', (e) => {
        e.preventDefault();
        dropBanner.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
}

// Export Trigger
function setupExport() {
    const btnExportPdf = document.getElementById('btn-export-pdf');
    const triggerExport = () => {
        const text = mdInput.value.trim();
        if (!text) {
            showToast("Please enter or upload Markdown content first.", "error");
            return;
        }

        if (!isEngineReady) {
            showToast("Engine is still loading WebAssembly, please wait...", "error");
            return;
        }

        if (btnExport) btnExport.disabled = true;
        if (btnHeaderExport) btnHeaderExport.disabled = true;
        if (btnToolbarExport) btnToolbarExport.disabled = true;
        if (btnText) btnText.innerText = "Generating DOCX...";
        showToast("Generating document locally in browser...", "success");

        const payload = {
            markdown: text,
            theme: selectedTheme,
            custom_theme: (selectedTheme === "custom") ? buildCustomThemeDictForDocx() : null,
            title: inpTitle.value.trim() || null,
            subtitle: inpSubtitle.value.trim() || null,
            author: inpAuthor.value.trim() || null,
            show_cover: chkCover.checked,
            show_toc: chkToc.checked,
            show_header: chkHeader ? chkHeader.checked : false,
            page_size: selPageSize.value
        };

        worker.postMessage({
            action: "CONVERT",
            id: Date.now(),
            payload
        });
    };

    const triggerTypstExport = () => {
        const text = mdInput.value.trim();
        if (!text) {
            showToast("Please enter or upload Markdown content first.", "error");
            return;
        }

        if (!isEngineReady) {
            showToast("Engine is still loading WebAssembly, please wait...", "error");
            return;
        }

        if (btnExportTypst) btnExportTypst.disabled = true;
        if (btnTypstText) btnTypstText.innerText = "Compiling Typst...";
        showToast("Compiling Typst vector document...", "success");

        const payload = {
            markdown: text,
            theme: selectedTheme,
            custom_theme: (selectedTheme === "custom") ? buildCustomThemeDictForDocx() : null,
            title: inpTitle.value.trim() || null,
            subtitle: inpSubtitle.value.trim() || null,
            author: inpAuthor.value.trim() || null,
            show_cover: chkCover.checked,
            show_toc: chkToc.checked,
            show_header: chkHeader ? chkHeader.checked : false,
            page_size: selPageSize.value
        };

        worker.postMessage({
            action: "CONVERT_TYPST",
            id: Date.now(),
            payload
        });
    };

    const triggerPrintPdf = () => {
        const text = mdInput.value.trim();
        if (!text) return showToast('Please enter or upload Markdown or text first.', 'error');
        const title = inpTitle.value.trim() || 'document';
        const opened = openPrintView(title, buildMarkdownPrintHtml(text), selPageSize.value);
        if (opened) showToast('Print view opened. Choose “Save as PDF” in the browser print dialog.', 'success');
    };

    if (btnExport) btnExport.addEventListener('click', triggerExport);
    if (btnExportPdf) btnExportPdf.addEventListener('click', triggerPrintPdf);
    if (btnHeaderExport) btnHeaderExport.addEventListener('click', triggerExport);
    if (btnToolbarExport) btnToolbarExport.addEventListener('click', triggerExport);
    if (btnExportTypst) btnExportTypst.addEventListener('click', triggerTypstExport);
}

function onTypstSuccess(typstSource) {
    if (btnExportTypst) btnExportTypst.disabled = false;
    if (btnTypstText) btnTypstText.innerText = "Download Typst source (.typ)";

    const blob = new Blob([typstSource], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    let docName = inpTitle.value.trim() || "document";
    docName = docName.replace(/[^a-zA-Z0-9_\-\s]/g, '').trim().replace(/\s+/g, '_');
    const fileName = `${docName || "document"}.typ`;

    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    a.remove();
    showToast(`Saved "${fileName}" ready for Typst compilation!`, "success");
}

function onExportSuccess(uint8Array) {
    if (btnExport) btnExport.disabled = false;
    if (btnHeaderExport) btnHeaderExport.disabled = false;
    if (btnToolbarExport) btnToolbarExport.disabled = false;
    if (btnText) btnText.innerText = "Download Word Document (.docx)";

    const blob = new Blob([uint8Array], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    const url = URL.createObjectURL(blob);
    
    let docName = inpTitle.value.trim() || "document";
    docName = docName.replace(/[^a-zA-Z0-9_\-\s]/g, '').trim().replace(/\s+/g, '_');
    const fileName = `${docName || "document"}.docx`;

    // Trigger automatic download
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    a.remove();

    // Show prominent direct download box
    if (downloadBox) {
        downloadBox.style.display = 'block';
        downloadBox.innerHTML = `
            <div class="download-box-text">Word document ready</div>
            <a href="${url}" download="${fileName}">Download again (${fileName})</a>
        `;
    }

    showToast(`Downloaded "${fileName}" successfully.`, "success");
}

function onExportError(errMsg) {
    if (btnExport) btnExport.disabled = false;
    if (btnHeaderExport) btnHeaderExport.disabled = false;
    if (btnToolbarExport) btnToolbarExport.disabled = false;
    if (btnText) btnText.innerText = "Download Word Document (.docx)";
    showToast("Conversion failed: " + errMsg, "error");
}

function showToast(msg, type) {
    statusToast.style.display = 'block';
    statusToast.className = `status-toast ${type}`;
    statusToast.innerText = msg;
}

// In-App Modal Dialog
let modalReturnFocus = null;

function showModal({ icon = "!", title = "Confirmation", message = "", confirmText = "Confirm", isDanger = false, onConfirm }) {
    const modal = document.getElementById('app-modal');
    const mIcon = document.getElementById('modal-icon');
    const mTitle = document.getElementById('modal-title');
    const mBody = document.getElementById('modal-body');
    const mCancel = document.getElementById('modal-btn-cancel');
    const mConfirm = document.getElementById('modal-btn-confirm');
    
    if (!modal) return;
    
    mIcon.innerText = icon;
    mTitle.innerText = title;
    mBody.innerText = message;
    mConfirm.innerText = confirmText;
    mConfirm.className = `modal-btn ${isDanger ? 'modal-btn-danger' : 'modal-btn-primary'}`;
    
    modalReturnFocus = document.activeElement;
    modal.style.display = 'flex';

    const handleModalKeydown = (event) => {
        if (event.key === 'Escape') {
            event.preventDefault();
            closeModal();
        } else if (event.key === 'Tab') {
            const focusables = [mCancel, mConfirm];
            const first = focusables[0];
            const last = focusables[focusables.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        }
    };
    
    const closeModal = () => {
        modal.style.display = 'none';
        modal.removeEventListener('keydown', handleModalKeydown);
        mConfirm.onclick = null;
        mCancel.onclick = null;
        if (modalReturnFocus && typeof modalReturnFocus.focus === 'function') modalReturnFocus.focus();
    };
    
    modal.addEventListener('keydown', handleModalKeydown);
    mCancel.focus();
    mCancel.onclick = closeModal;
    mConfirm.onclick = () => {
        closeModal();
        if (onConfirm) onConfirm();
    };
    modal.onclick = (e) => {
        if (e.target === modal) closeModal();
    };
}

// Event Listeners & Boot
document.addEventListener('DOMContentLoaded', () => {
    initWorker();
    setupTabs();
    setupFileUpload();
    setupExport();
    setupCustomThemeListeners();
    setupDropZoneAccessibility();

    // Theme card clicks
    document.querySelectorAll('.theme-option').forEach(card => {
        card.addEventListener('click', () => {
            selectTheme(card.dataset.theme);
            scheduleDraftSave();
        });
        card.addEventListener('keydown', (event) => {
            const cards = [...document.querySelectorAll('.theme-option')];
            const current = cards.indexOf(card);
            let next = current;
            if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (current + 1) % cards.length;
            else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (current - 1 + cards.length) % cards.length;
            else if (event.key === ' ' || event.key === 'Enter') next = current;
            else return;
            event.preventDefault();
            selectTheme(cards[next].dataset.theme);
            cards[next].focus();
            scheduleDraftSave();
        });
    });

    // Sample button
    btnSample.addEventListener('click', () => {
        loadMarkdownDocument(SAMPLE_MARKDOWN);
        showToast("Loaded sample document.", "success");
    });

    // Clear button with In-App Modal Dialog
    btnClear.addEventListener('click', () => {
        showModal({
            icon: "!",
            title: "Clear Editor Content?",
            message: "Are you sure you want to clear all Markdown content? This action cannot be undone.",
            confirmText: "Yes, Clear All",
            isDanger: true,
            onConfirm: () => {
                mdInput.value = "";
                updatePreview();
                saveDraft();
                setDraftStatus('Empty draft saved on this device');
                showToast("Editor content cleared.", "success");
            }
        });
    });

    // Auto-update preview on typing (debounced)
    let debounceTimer = null;
    mdInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(updatePreview, 300);
        scheduleDraftSave();
    });

    // Auto-update preview when metadata or toggles change
    [inpTitle, inpSubtitle, inpAuthor].forEach(el => {
        el.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(updatePreview, 150);
            scheduleDraftSave();
        });
    });
    [chkCover, chkToc, chkHeader, selPageSize].forEach(el => {
        el.addEventListener('change', () => {
            if (el === chkCover) updatePreview();
            scheduleDraftSave();
        });
    });

    // Multi-Mode Studio Setups
    setupStudioNavigation();
    setupDocxConverter();
    setupHtmlMarkdownConverter();
    setupPdfToolbox();

    // Initial setup
    updateCustomSwatches();
    if (!restoreDraft()) {
        loadMarkdownDocument(SAMPLE_MARKDOWN);
        saveDraft();
    }
    updatePreview();
});

// ==========================================================================
// STUDIO MODE NAVIGATION
// ==========================================================================
function setupStudioNavigation() {
    const btnModeMd = document.getElementById('btn-mode-markdown');
    const btnModeDocx = document.getElementById('btn-mode-docx');
    const btnModePdf = document.getElementById('btn-mode-pdf');
    const btnModeHtml = document.getElementById('btn-mode-html');

    const viewMd = document.getElementById('view-mode-markdown');
    const viewDocx = document.getElementById('view-mode-docx');
    const viewPdf = document.getElementById('view-mode-pdf');
    const viewHtml = document.getElementById('view-mode-html');
    const buttons = [btnModeMd, btnModeDocx, btnModePdf, btnModeHtml];
    const views = [viewMd, viewDocx, viewPdf, viewHtml];
    const modes = ['markdown', 'docx', 'pdf', 'html'];

    const switchMode = (mode) => {
        const activeIndex = modes.indexOf(mode);
        if (activeIndex < 0) return;
        buttons.forEach((button, index) => {
            if (!button) return;
            const selected = index === activeIndex;
            button.classList.toggle('active', selected);
            button.setAttribute('aria-selected', String(selected));
            button.tabIndex = selected ? 0 : -1;
        });
        views.forEach((view, index) => {
            if (!view) return;
            const selected = index === activeIndex;
            view.style.display = selected ? 'block' : 'none';
            view.setAttribute('aria-hidden', String(!selected));
        });
    };

    buttons.forEach((button, index) => {
        if (!button) return;
        button.addEventListener('click', () => switchMode(modes[index]));
        button.addEventListener('keydown', (event) => {
            if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
            event.preventDefault();
            const delta = event.key === 'ArrowRight' ? 1 : -1;
            const nextIndex = (index + delta + buttons.length) % buttons.length;
            buttons[nextIndex].click();
            buttons[nextIndex].focus();
        });
    });
    switchMode('markdown');
}

// ==========================================================================
// CLIENT-SIDE WORD (.DOCX) TO MARKDOWN CONVERTER (MAMMOTH + GFM)
// ==========================================================================
function setupDocxConverter() {
    const dropZone = document.getElementById('docx-drop-zone');
    const fileInput = document.getElementById('docx-file-input');
    const outputArea = document.getElementById('docx-markdown-output');
    const statsBar = document.getElementById('docx-stats-bar');
    const statFilename = document.getElementById('stat-filename');
    const statWords = document.getElementById('stat-words');
    const statHeadings = document.getElementById('stat-headings');
    const statTables = document.getElementById('stat-tables');

    const btnCopy = document.getElementById('btn-copy-docx-md');
    const btnDownload = document.getElementById('btn-download-docx-md');
    const btnDocxToPdf = document.getElementById('btn-docx-to-pdf');
    const btnOpenInStudio = document.getElementById('btn-open-in-studio');
    let latestDocxHtml = '';
    let latestDocxName = 'document';

    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleDocxFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleDocxFile(e.target.files[0]);
        e.target.value = '';
    });

    const handleDocxFile = async (file) => {
        if (!file.name.toLowerCase().endsWith('.docx')) {
            showToast("Please select a valid Microsoft Word (.docx) document.", "error");
            return;
        }

        latestDocxHtml = '';
        latestDocxName = file.name.replace(/\.docx$/i, '') || 'document';

        showToast(`Converting "${file.name}" locally in browser...`, "success");

        try {
            const arrayBuffer = await file.arrayBuffer();
            if (!window.mammoth) {
                showToast("Mammoth engine not loaded yet, please try again.", "error");
                return;
            }

            const customStyleMap = [
                "p[style-name^='Heading 1'] => h1:fresh",
                "p[style-name^='Heading 2'] => h2:fresh",
                "p[style-name^='Heading 3'] => h3:fresh",
                "p[style-name^='Heading 4'] => h4:fresh",
                "p[style-name='Title'] => h1:fresh",
                "p[style-name='Subtitle'] => h2:fresh"
            ];

            const result = await mammoth.convertToHtml({ arrayBuffer }, { styleMap: customStyleMap });
            const rawHtml = result.value || "";

            // Sanitize with DOMPurify
            const cleanHtml = window.DOMPurify ? DOMPurify.sanitize(rawHtml) : rawHtml;
            latestDocxHtml = cleanHtml;
            latestDocxName = file.name.replace(/\.docx$/i, '') || 'document';

            // Convert to Markdown with Turndown + GFM plugin
            const turndownService = new TurndownService({
                headingStyle: 'atx',
                codeBlockStyle: 'fenced'
            });
            if (window.turndownPluginGfm && turndownService.use) {
                turndownService.use(turndownPluginGfm.gfm);
            }

            let mdText = turndownService.turndown(cleanHtml);
            outputArea.value = mdText;

            // Stats
            const words = mdText.trim() ? mdText.trim().split(/\s+/).length : 0;
            const headings = (mdText.match(/^#{1,6}\s+/gm) || []).length;
            const tables = (mdText.match(/\|[\s-:]+\|/g) || []).length;

            if (statsBar) statsBar.style.display = 'flex';
            if (statFilename) statFilename.innerText = file.name;
            if (statWords) statWords.innerText = words.toLocaleString();
            if (statHeadings) statHeadings.innerText = headings;
            if (statTables) statTables.innerText = tables;

            showToast("DOCX converted to clean Markdown!", "success");
        } catch (err) {
            console.error("DOCX Conversion error:", err);
            showToast("Failed to parse Word document: " + err.message, "error");
        }
    };

    if (btnCopy) {
        btnCopy.addEventListener('click', () => {
            if (!outputArea.value.trim()) return showToast("No Markdown to copy.", "error");
            navigator.clipboard.writeText(outputArea.value);
            showToast("Copied Markdown to clipboard!", "success");
        });
    }

    if (btnDownload) {
        btnDownload.addEventListener('click', () => {
            const text = outputArea.value.trim();
            if (!text) return showToast("No Markdown to download.", "error");
            const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = (statFilename.innerText.replace(/\.docx$/i, '') || "converted") + ".md";
            a.click();
            a.remove();
        });
    }

    if (btnDocxToPdf) {
        btnDocxToPdf.addEventListener('click', () => {
            if (!latestDocxHtml) return showToast('Open a Word document first.', 'error');
            const opened = openPrintView(latestDocxName, latestDocxHtml, 'A4');
            if (opened) showToast('Word content opened as a print-ready reconstruction. Choose “Save as PDF” to export.', 'success');
        });
    }

    if (btnOpenInStudio) {
        btnOpenInStudio.addEventListener('click', () => {
            const text = outputArea.value.trim();
            if (!text) return showToast("No Markdown to load into Studio.", "error");
            loadMarkdownDocument(text);
            document.getElementById('btn-mode-markdown').click();
            showToast("Document opened in Markdown Studio!", "success");
        });
    }
}

// ==========================================================================
// CLIENT-SIDE HTML ↔ MARKDOWN CONVERTER
// ========================================================================
function setupHtmlMarkdownConverter() {
    const direction = document.getElementById('html-convert-direction');
    const fileInput = document.getElementById('conversion-file-input');
    const openFile = document.getElementById('btn-open-conversion-file');
    const source = document.getElementById('conversion-source');
    const output = document.getElementById('conversion-output');
    const sourceLabel = document.getElementById('conversion-source-label');
    const outputLabel = document.getElementById('conversion-output-label');
    const hint = document.getElementById('conversion-hint');
    const btnConvert = document.getElementById('btn-run-conversion');
    const btnCopy = document.getElementById('btn-copy-conversion');
    const btnDownload = document.getElementById('btn-download-conversion');
    const btnOpenInStudio = document.getElementById('btn-open-conversion-in-studio');
    let sourceName = 'converted';

    if (!direction || !fileInput || !source || !output) return;

    const isHtmlToMarkdown = () => direction.value === 'html-to-md';
    const updateDirection = (reset = false) => {
        const htmlToMd = isHtmlToMarkdown();
        sourceLabel.textContent = htmlToMd ? 'HTML source' : 'Markdown source';
        outputLabel.textContent = htmlToMd ? 'Markdown result' : 'HTML document';
        source.placeholder = htmlToMd ? 'Paste HTML here, or open an .html file…' : 'Write or paste Markdown here, or open an .md or .txt file…';
        fileInput.accept = htmlToMd ? '.html,.htm,.xhtml,text/html' : '.md,.markdown,.txt,text/plain';
        hint.textContent = htmlToMd
            ? 'HTML styling is simplified to semantic Markdown. Linked assets remain references to their original locations.'
            : 'Creates a self-contained HTML document with readable typography and safe, sanitized content.';
        btnOpenInStudio.hidden = !htmlToMd;
        if (reset) {
            source.value = '';
            output.value = '';
            sourceName = 'converted';
        }
    };

    direction.addEventListener('change', () => updateDirection(true));
    openFile.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (event) => {
        const file = event.target.files && event.target.files[0];
        if (!file) return;
        const expected = isHtmlToMarkdown() ? /\.(html?|xhtml)$/i : /\.(md|markdown|txt)$/i;
        if (!expected.test(file.name)) {
            showToast(isHtmlToMarkdown() ? 'Choose an HTML file (.html, .htm, .xhtml).' : 'Choose a Markdown or text file (.md, .markdown, .txt).', 'error');
            event.target.value = '';
            return;
        }
        const reader = new FileReader();
        reader.onload = () => {
            source.value = String(reader.result || '');
            output.value = '';
            sourceName = file.name.replace(/\.(html?|xhtml|markdown|md|txt)$/i, '') || 'converted';
            showToast(`Loaded "${file.name}"`, 'success');
        };
        reader.onerror = () => showToast('Could not read this file.', 'error');
        reader.readAsText(file);
        event.target.value = '';
    });

    btnConvert.addEventListener('click', () => {
        const text = source.value.trim();
        if (!text) return showToast('Paste content or open a file first.', 'error');
        try {
            if (isHtmlToMarkdown()) {
                if (!window.TurndownService) throw new Error('HTML conversion engine is not loaded. Check your connection and reload the page.');
                const safeHtml = window.DOMPurify ? DOMPurify.sanitize(text) : text;
                const turndown = new TurndownService({ headingStyle: 'atx', codeBlockStyle: 'fenced' });
                if (window.turndownPluginGfm && turndown.use) turndown.use(turndownPluginGfm.gfm);
                output.value = turndown.turndown(safeHtml).trim();
            } else {
                if (!window.marked) throw new Error('Markdown conversion engine is not loaded. Check your connection and reload the page.');
                const markdownSource = text.replace(/^---\s*[\r\n]+[\s\S]*?[\r\n]+---\s*[\r\n]+/, '');
                const body = marked.parse(markdownSource);
                const safeBody = window.DOMPurify ? DOMPurify.sanitize(body) : body;
                const title = escapeHtml(sourceName.replace(/[_-]+/g, ' '));
                output.value = `<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>${title}</title>\n<style>body{max-width:820px;margin:48px auto;padding:0 24px;color:#243443;font:16px/1.7 Segoe UI,Arial,sans-serif}h1,h2,h3{color:#183b56;line-height:1.25}h2{border-bottom:1px solid #d8e1e6;padding-bottom:.25em}a{color:#146e74}blockquote{border-left:3px solid #147d79;margin-left:0;padding:.2em 1em;color:#526574;background:#f5f8f8}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f7;border:1px solid #dfe6e9;padding:12px}code{font-family:Consolas,monospace;background:#f1f4f5;padding:.12em .28em}table{width:100%;border-collapse:collapse}th,td{border:1px solid #cbd6dc;padding:7px 9px;text-align:left}th{background:#183b56;color:#fff}img{max-width:100%;height:auto}</style>\n</head>\n<body>\n${safeBody}\n</body>\n</html>`;
            }
            showToast('Conversion complete.', 'success');
        } catch (err) {
            console.error('HTML / Markdown conversion failed:', err);
            showToast(err.message || 'Conversion failed.', 'error');
        }
    });

    btnCopy.addEventListener('click', async () => {
        if (!output.value.trim()) return showToast('Convert some content first.', 'error');
        try {
            await navigator.clipboard.writeText(output.value);
        } catch (err) {
            output.focus();
            output.select();
            document.execCommand('copy');
        }
        showToast('Result copied to clipboard.', 'success');
    });

    btnDownload.addEventListener('click', () => {
        if (!output.value.trim()) return showToast('Convert some content first.', 'error');
        const extension = isHtmlToMarkdown() ? '.md' : '.html';
        const mime = isHtmlToMarkdown() ? 'text/markdown;charset=utf-8' : 'text/html;charset=utf-8';
        const blob = new Blob([output.value], { type: mime });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = `${sourceName}${extension}`;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    });

    btnOpenInStudio.addEventListener('click', () => {
        if (!isHtmlToMarkdown() || !output.value.trim()) return showToast('Convert HTML to Markdown first.', 'error');
        loadMarkdownDocument(output.value);
        document.getElementById('btn-mode-markdown').click();
        showToast('Markdown opened in the editor.', 'success');
    });

    updateDirection();
}

// CLIENT-SIDE PDF TOOLBOX (PDF.JS, PDF-LIB, JSZIP)
// ==========================================================================
function setupPdfToolbox() {
    // Subtabs
    const subtabs = document.querySelectorAll('.pdf-subtab-btn');
    subtabs.forEach(btn => {
        btn.addEventListener('click', () => {
            subtabs.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            subtabs.forEach(b => {
                const selected = b === btn;
                b.setAttribute('aria-selected', String(selected));
                b.tabIndex = selected ? 0 : -1;
            });
            const sub = btn.dataset.sub;
            document.querySelectorAll('.pdf-panel-content').forEach(p => {
                p.style.display = 'none';
                p.setAttribute('aria-hidden', 'true');
            });
            const target = document.getElementById(`pdf-panel-${sub}`);
            if (target) {
                target.style.display = 'block';
                target.setAttribute('aria-hidden', 'false');
            }
        });
        btn.addEventListener('keydown', (event) => {
            if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
            event.preventDefault();
            const current = [...subtabs].indexOf(btn);
            const delta = event.key === 'ArrowRight' ? 1 : -1;
            const next = subtabs[(current + delta + subtabs.length) % subtabs.length];
            next.click();
            next.focus();
        });
    });

    // Tool 1: PDF to Images
    const p2iDrop = document.getElementById('pdf2img-drop-zone');
    const p2iInput = document.getElementById('pdf2img-file-input');
    const p2iGrid = document.getElementById('pdf2img-thumbnails-grid');
    const p2iActionBar = document.getElementById('pdf2img-action-bar');
    const p2iStatus = document.getElementById('pdf2img-status-text');
    const btnZip = document.getElementById('btn-download-all-zip');

    let renderedPngBlobs = [];

    if (p2iDrop && p2iInput) {
        p2iDrop.addEventListener('click', () => p2iInput.click());
        p2iDrop.addEventListener('dragover', (e) => { e.preventDefault(); p2iDrop.classList.add('dragover'); });
        p2iDrop.addEventListener('dragleave', () => p2iDrop.classList.remove('dragover'));
        p2iDrop.addEventListener('drop', (e) => {
            e.preventDefault();
            p2iDrop.classList.remove('dragover');
            if (e.dataTransfer.files.length) renderPdfToImages(e.dataTransfer.files[0]);
        });
        p2iInput.addEventListener('change', (e) => {
            if (e.target.files.length) renderPdfToImages(e.target.files[0]);
        });
    }

    async function renderPdfToImages(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showToast("Please select a PDF document.", "error");
            return;
        }
        showToast("Rendering PDF pages in browser memory...", "success");
        p2iGrid.innerHTML = "";
        renderedPngBlobs = [];

        try {
            const arrayBuffer = await file.arrayBuffer();
            const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
            const pdfDoc = await loadingTask.promise;

            p2iActionBar.style.display = 'flex';
            p2iStatus.innerText = `${file.name} • ${pdfDoc.numPages} pages`;

            for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
                const page = await pdfDoc.getPage(pageNum);
                const viewport = page.getViewport({ scale: 1.5 });

                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = viewport.width;
                canvas.height = viewport.height;

                await page.render({ canvasContext: ctx, viewport }).promise;

                const dataUrl = canvas.toDataURL('image/png');
                const blob = await new Promise(res => canvas.toBlob(res, 'image/png'));
                renderedPngBlobs.push({ pageNum, blob, dataUrl });

                const card = document.createElement('div');
                card.className = 'page-thumb-card';
                card.innerHTML = `
                    <div class="page-thumb-meta">
                        <span>Page ${pageNum}</span>
                        <button class="btn-thumb-download" data-page="${pageNum}">Save PNG</button>
                    </div>
                `;
                card.insertBefore(canvas, card.firstChild);
                card.querySelector('.btn-thumb-download').onclick = () => {
                    const a = document.createElement('a');
                    a.href = dataUrl;
                    a.download = `page_${String(pageNum).padStart(3, '0')}.png`;
                    a.click();
                };
                p2iGrid.appendChild(card);
            }
            showToast(`Rendered ${pdfDoc.numPages} pages successfully!`, "success");
        } catch (err) {
            console.error("PDF Render Error:", err);
            showToast("Failed to render PDF: " + err.message, "error");
        }
    }

    if (btnZip) {
        btnZip.addEventListener('click', async () => {
            if (!renderedPngBlobs.length) return;
            showToast("Packaging PNGs into ZIP...", "success");
            const zip = new JSZip();
            renderedPngBlobs.forEach(item => {
                zip.file(`page_${String(item.pageNum).padStart(3, '0')}.png`, item.blob);
            });
            const content = await zip.generateAsync({ type: "blob" });
            const url = URL.createObjectURL(content);
            const a = document.createElement('a');
            a.href = url;
            a.download = "extracted_pdf_pages.zip";
            a.click();
            a.remove();
            showToast("Downloaded all pages as ZIP!", "success");
        });
    }

    // Tool 2: Images to PDF
    const i2pDrop = document.getElementById('img2pdf-drop-zone');
    const i2pInput = document.getElementById('img2pdf-file-input');
    const i2pActionBar = document.getElementById('img2pdf-action-bar');
    const i2pStatus = document.getElementById('img2pdf-status-text');
    const i2pGrid = document.getElementById('img2pdf-preview-grid');
    const i2pOrderHint = document.getElementById('img2pdf-order-hint');
    const btnAddImagesPdf = document.getElementById('btn-add-images-pdf');
    const btnCompilePdf = document.getElementById('btn-compile-images-pdf');

    let loadedImages = [];
    let nextImageId = 1;

    if (i2pDrop && i2pInput) {
        i2pDrop.addEventListener('click', () => i2pInput.click());
        i2pDrop.addEventListener('dragover', (e) => { e.preventDefault(); i2pDrop.classList.add('dragover'); });
        i2pDrop.addEventListener('dragleave', () => i2pDrop.classList.remove('dragover'));
        i2pDrop.addEventListener('drop', (e) => {
            e.preventDefault();
            i2pDrop.classList.remove('dragover');
            handleLoadedImages(Array.from(e.dataTransfer.files));
        });
        i2pInput.addEventListener('change', (e) => {
            handleLoadedImages(Array.from(e.target.files));
            i2pInput.value = '';
        });
    }

    if (btnAddImagesPdf && i2pInput) {
        btnAddImagesPdf.addEventListener('click', () => i2pInput.click());
    }

    function handleLoadedImages(files) {
        const valid = files.filter(file => file.type.startsWith('image/') || /\.(png|jpe?g|gif|webp|bmp|avif)$/i.test(file.name));
        if (!valid.length) return showToast("Please select valid image files.", "error");
        const added = valid.map(file => ({ id: nextImageId++, file, previewUrl: URL.createObjectURL(file) }));
        loadedImages.push(...added);
        renderImagesList();
        if (valid.length < files.length) {
            showToast(`Added ${valid.length} image${valid.length === 1 ? '' : 's'}; skipped ${files.length - valid.length} unsupported file${files.length - valid.length === 1 ? '' : 's'}.`, "success");
        } else {
            showToast(`Added ${valid.length} image${valid.length === 1 ? '' : 's'}.`, "success");
        }
    }

    function renderImagesList() {
        const imageCount = loadedImages.length;
        i2pActionBar.style.display = imageCount ? 'flex' : 'none';
        i2pOrderHint.hidden = !imageCount;
        i2pStatus.innerText = `${imageCount} image${imageCount === 1 ? '' : 's'} queued`;
        btnCompilePdf.disabled = !imageCount;
        i2pGrid.innerHTML = "";
        loadedImages.forEach((entry, idx) => {
            const file = entry.file;
            const item = document.createElement('article');
            item.className = 'image-page-card';
            item.setAttribute('role', 'listitem');
            item.setAttribute('aria-label', `Page ${idx + 1}: ${file.name}`);
            item.draggable = true;

            const preview = document.createElement('div');
            preview.className = 'image-page-preview';
            const image = document.createElement('img');
            image.src = entry.previewUrl;
            image.alt = `Preview of ${file.name}`;
            image.loading = 'lazy';
            preview.appendChild(image);

            const pageNumber = document.createElement('span');
            pageNumber.className = 'image-page-number';
            pageNumber.textContent = `Page ${String(idx + 1).padStart(2, '0')}`;
            preview.appendChild(pageNumber);

            const details = document.createElement('div');
            details.className = 'image-page-details';
            const filename = document.createElement('strong');
            filename.className = 'image-page-filename';
            filename.textContent = file.name;
            filename.title = file.name;
            const fileSize = document.createElement('span');
            fileSize.className = 'image-page-size';
            fileSize.textContent = `${(file.size / 1024).toFixed(1)} KB`;
            details.append(filename, fileSize);

            const actions = document.createElement('div');
            actions.className = 'image-page-actions';
            const moveUp = document.createElement('button');
            moveUp.type = 'button';
            moveUp.className = 'image-order-button';
            moveUp.textContent = '↑';
            moveUp.title = 'Move page earlier';
            moveUp.setAttribute('aria-label', `Move ${file.name} earlier`);
            moveUp.disabled = idx === 0;
            moveUp.addEventListener('click', () => moveImage(idx, -1));

            const moveDown = document.createElement('button');
            moveDown.type = 'button';
            moveDown.className = 'image-order-button';
            moveDown.textContent = '↓';
            moveDown.title = 'Move page later';
            moveDown.setAttribute('aria-label', `Move ${file.name} later`);
            moveDown.disabled = idx === imageCount - 1;
            moveDown.addEventListener('click', () => moveImage(idx, 1));

            const removeButton = document.createElement('button');
            removeButton.type = 'button';
            removeButton.className = 'image-remove-button';
            removeButton.textContent = 'Remove';
            removeButton.addEventListener('click', () => removeImage(entry.id));

            actions.append(moveUp, moveDown, removeButton);
            item.append(preview, details, actions);

            item.addEventListener('dragstart', (event) => {
                item.classList.add('is-dragging');
                event.dataTransfer.effectAllowed = 'move';
                event.dataTransfer.setData('text/plain', String(entry.id));
            });
            item.addEventListener('dragend', () => {
                item.classList.remove('is-dragging');
                i2pGrid.querySelectorAll('.drop-target').forEach(card => card.classList.remove('drop-target'));
            });
            item.addEventListener('dragover', (event) => {
                event.preventDefault();
                event.dataTransfer.dropEffect = 'move';
                item.classList.add('drop-target');
            });
            item.addEventListener('dragleave', (event) => {
                if (!item.contains(event.relatedTarget)) item.classList.remove('drop-target');
            });
            item.addEventListener('drop', (event) => {
                event.preventDefault();
                item.classList.remove('drop-target');
                const draggedId = Number(event.dataTransfer.getData('text/plain'));
                const fromIndex = loadedImages.findIndex(imageEntry => imageEntry.id === draggedId);
                const toIndex = loadedImages.findIndex(imageEntry => imageEntry.id === entry.id);
                if (fromIndex < 0 || toIndex < 0 || fromIndex === toIndex) return;
                const [draggedImage] = loadedImages.splice(fromIndex, 1);
                loadedImages.splice(toIndex, 0, draggedImage);
                renderImagesList();
            });

            i2pGrid.appendChild(item);
        });
    }

    function moveImage(index, direction) {
        const targetIndex = index + direction;
        if (targetIndex < 0 || targetIndex >= loadedImages.length) return;
        [loadedImages[index], loadedImages[targetIndex]] = [loadedImages[targetIndex], loadedImages[index]];
        renderImagesList();
    }

    function removeImage(imageId) {
        const imageIndex = loadedImages.findIndex(entry => entry.id === imageId);
        if (imageIndex < 0) return;
        URL.revokeObjectURL(loadedImages[imageIndex].previewUrl);
        loadedImages.splice(imageIndex, 1);
        renderImagesList();
    }

    async function convertImageToPngBytes(file) {
        const image = new Image();
        const objectUrl = URL.createObjectURL(file);
        try {
            await new Promise((resolve, reject) => {
                image.onload = resolve;
                image.onerror = () => reject(new Error(`Could not read ${file.name} as an image.`));
                image.src = objectUrl;
            });
            const canvas = document.createElement('canvas');
            canvas.width = image.naturalWidth;
            canvas.height = image.naturalHeight;
            const context = canvas.getContext('2d');
            if (!context) throw new Error(`Could not prepare ${file.name} for PDF.`);
            context.drawImage(image, 0, 0);
            const pngBlob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
            if (!pngBlob) throw new Error(`Could not convert ${file.name} to a PDF-compatible image.`);
            return await pngBlob.arrayBuffer();
        } finally {
            URL.revokeObjectURL(objectUrl);
        }
    }

    if (btnCompilePdf) {
        btnCompilePdf.addEventListener('click', async () => {
            if (!loadedImages.length) return showToast("Please add images first.", "error");
            btnCompilePdf.disabled = true;
            btnCompilePdf.textContent = "Generating PDF...";
            showToast("Compiling PDF in browser memory...", "success");
            try {
                const pdfDoc = await PDFLib.PDFDocument.create();
                for (const entry of loadedImages) {
                    const imgFile = entry.file;
                    const bytes = await imgFile.arrayBuffer();
                    let embedded;
                    const fileExtension = imgFile.name.toLowerCase().split('.').pop();
                    if (imgFile.type.toLowerCase() === 'image/png' || fileExtension === 'png') {
                        embedded = await pdfDoc.embedPng(bytes);
                    } else if (imgFile.type.toLowerCase() === 'image/jpeg' || ['jpg', 'jpeg'].includes(fileExtension)) {
                        embedded = await pdfDoc.embedJpg(bytes);
                    } else {
                        embedded = await pdfDoc.embedPng(await convertImageToPngBytes(imgFile));
                    }
                    const page = pdfDoc.addPage([embedded.width, embedded.height]);
                    page.drawImage(embedded, {
                        x: 0,
                        y: 0,
                        width: embedded.width,
                        height: embedded.height
                    });
                }
                const pdfBytes = await pdfDoc.save();
                const blob = new Blob([pdfBytes], { type: "application/pdf" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = "compiled_images.pdf";
                a.click();
                a.remove();
                showToast("PDF generated and downloaded!", "success");
            } catch (err) {
                console.error("PDF Compile Error:", err);
                showToast("Failed to compile PDF: " + err.message, "error");
            } finally {
                btnCompilePdf.disabled = loadedImages.length === 0;
                btnCompilePdf.textContent = "Generate & download PDF";
            }
        });
    }

    // Tool 3: Merge PDFs
    const mDrop = document.getElementById('merge-drop-zone');
    const mInput = document.getElementById('merge-file-input');
    const mActionBar = document.getElementById('merge-action-bar');
    const mStatus = document.getElementById('merge-status-text');
    const mQueue = document.getElementById('merge-queue-list');
    const btnExecMerge = document.getElementById('btn-execute-merge');

    let pdfFilesToMerge = [];

    if (mDrop && mInput) {
        mDrop.addEventListener('click', () => mInput.click());
        mDrop.addEventListener('dragover', (e) => { e.preventDefault(); mDrop.classList.add('dragover'); });
        mDrop.addEventListener('dragleave', () => mDrop.classList.remove('dragover'));
        mDrop.addEventListener('drop', (e) => {
            e.preventDefault();
            mDrop.classList.remove('dragover');
            handlePdfsToMerge(Array.from(e.dataTransfer.files));
        });
        mInput.addEventListener('change', (e) => {
            handlePdfsToMerge(Array.from(e.target.files));
        });
    }

    function handlePdfsToMerge(files) {
        const valid = files.filter(f => f.name.toLowerCase().endsWith('.pdf'));
        if (!valid.length) return showToast("Please select valid .pdf files.", "error");
        pdfFilesToMerge.push(...valid);
        mActionBar.style.display = 'flex';
        mStatus.innerText = `${pdfFilesToMerge.length} PDFs queued`;
        renderMergeQueue();
        showToast(`Added ${valid.length} PDF files to merge!`, "success");
    }

    function renderMergeQueue() {
        mQueue.innerHTML = "";
        pdfFilesToMerge.forEach((pdf, idx) => {
            const li = document.createElement('li');
            li.className = 'queue-item';
            const label = document.createElement('span');
            const filename = document.createElement('strong');
            filename.textContent = pdf.name;
            label.append(`Document ${idx + 1}: `, filename, ` (${(pdf.size / 1024).toFixed(1)} KB)`);
            const removeButton = document.createElement('button');
            removeButton.type = 'button';
            removeButton.className = 'action-btn';
            removeButton.style.color = '#b42318';
            removeButton.textContent = 'Remove';
            removeButton.onclick = () => {
                pdfFilesToMerge.splice(idx, 1);
                renderMergeQueue();
                mStatus.innerText = `${pdfFilesToMerge.length} PDFs queued`;
            };
            li.append(label, removeButton);
            mQueue.appendChild(li);
        });
    }

    if (btnExecMerge) {
        btnExecMerge.addEventListener('click', async () => {
            if (pdfFilesToMerge.length < 2) return showToast("Please add at least 2 PDF files to merge.", "error");
            showToast("Merging PDFs in browser memory...", "success");
            try {
                const mergedDoc = await PDFLib.PDFDocument.create();
                for (const pdfFile of pdfFilesToMerge) {
                    const bytes = await pdfFile.arrayBuffer();
                    const srcDoc = await PDFLib.PDFDocument.load(bytes);
                    const copiedPages = await mergedDoc.copyPages(srcDoc, srcDoc.getPageIndices());
                    copiedPages.forEach(page => mergedDoc.addPage(page));
                }
                const mergedBytes = await mergedDoc.save();
                const blob = new Blob([mergedBytes], { type: "application/pdf" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = "merged_document.pdf";
                a.click();
                a.remove();
                showToast("Merged PDF created successfully!", "success");
            } catch (err) {
                console.error("PDF Merge Error:", err);
                showToast("Failed to merge PDFs: " + err.message, "error");
            }
        });
    }

    // Tool 4: Split PDF
    const sDrop = document.getElementById('split-drop-zone');
    const sInput = document.getElementById('split-file-input');
    const sActionBar = document.getElementById('split-action-bar');
    const sStatus = document.getElementById('split-status-text');
    const selSplitMode = document.getElementById('sel-split-mode');
    const inpSplitRange = document.getElementById('inp-split-range');
    const btnExecSplit = document.getElementById('btn-execute-split');

    let loadedSplitFile = null;
    let loadedSplitBytes = null;

    if (sDrop && sInput) {
        sDrop.addEventListener('click', () => sInput.click());
        sDrop.addEventListener('dragover', (e) => { e.preventDefault(); sDrop.classList.add('dragover'); });
        sDrop.addEventListener('dragleave', () => sDrop.classList.remove('dragover'));
        sDrop.addEventListener('drop', (e) => {
            e.preventDefault();
            sDrop.classList.remove('dragover');
            if (e.dataTransfer.files.length) handleSplitDoc(e.dataTransfer.files[0]);
        });
        sInput.addEventListener('change', (e) => {
            if (e.target.files.length) handleSplitDoc(e.target.files[0]);
        });
    }

    if (selSplitMode && inpSplitRange) {
        selSplitMode.addEventListener('change', () => {
            if (selSplitMode.value === 'range') {
                inpSplitRange.style.display = 'inline-block';
            } else {
                inpSplitRange.style.display = 'none';
            }
        });
    }

    async function handleSplitDoc(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            return showToast("Please select a PDF document.", "error");
        }
        try {
            loadedSplitBytes = await file.arrayBuffer();
            const srcDoc = await PDFLib.PDFDocument.load(loadedSplitBytes);
            loadedSplitFile = file;
            sActionBar.style.display = 'flex';
            sStatus.innerText = `${file.name} • ${srcDoc.getPageCount()} pages`;
            showToast(`Loaded ${file.name} (${srcDoc.getPageCount()} pages)`, "success");
        } catch (err) {
            console.error("PDF Load Error:", err);
            showToast("Failed to load PDF: " + err.message, "error");
        }
    }

    if (btnExecSplit) {
        btnExecSplit.addEventListener('click', async () => {
            if (!loadedSplitFile || !loadedSplitBytes) return showToast("Please select a PDF to split first.", "error");
            showToast("Processing PDF split in browser memory...", "success");
            try {
                const srcDoc = await PDFLib.PDFDocument.load(loadedSplitBytes);
                const totalPages = srcDoc.getPageCount();
                const baseName = loadedSplitFile.name.replace(/\.pdf$/i, '');

                if (selSplitMode.value === 'all') {
                    const zip = new JSZip();
                    for (let i = 0; i < totalPages; i++) {
                        const singleDoc = await PDFLib.PDFDocument.create();
                        const [copiedPage] = await singleDoc.copyPages(srcDoc, [i]);
                        singleDoc.addPage(copiedPage);
                        const singleBytes = await singleDoc.save();
                        zip.file(`${baseName}_page_${String(i + 1).padStart(3, '0')}.pdf`, singleBytes);
                    }
                    const content = await zip.generateAsync({ type: "blob" });
                    const url = URL.createObjectURL(content);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${baseName}_split_pages.zip`;
                    a.click();
                    a.remove();
                    showToast(`Successfully extracted ${totalPages} pages into ZIP!`, "success");
                } else {
                    // Custom range, e.g. "1-3, 5"
                    const rangeStr = inpSplitRange.value.trim();
                    if (!rangeStr) return showToast("Please specify page numbers (e.g. 1-3).", "error");

                    const pagesToExtract = new Set();
                    const parts = rangeStr.split(',');
                    for (const part of parts) {
                        const trimmed = part.trim();
                        if (trimmed.includes('-')) {
                            const [start, end] = trimmed.split('-').map(x => parseInt(x.trim(), 10));
                            if (!isNaN(start) && !isNaN(end)) {
                                for (let p = Math.max(1, start); p <= Math.min(totalPages, end); p++) {
                                    pagesToExtract.add(p - 1);
                                }
                            }
                        } else {
                            const p = parseInt(trimmed, 10);
                            if (!isNaN(p) && p >= 1 && p <= totalPages) {
                                pagesToExtract.add(p - 1);
                            }
                        }
                    }

                    const sortedIndices = Array.from(pagesToExtract).sort((a, b) => a - b);
                    if (!sortedIndices.length) return showToast("No valid page numbers found in range.", "error");

                    const rangeDoc = await PDFLib.PDFDocument.create();
                    const copiedPages = await rangeDoc.copyPages(srcDoc, sortedIndices);
                    copiedPages.forEach(p => rangeDoc.addPage(p));
                    const rangeBytes = await rangeDoc.save();
                    const blob = new Blob([rangeBytes], { type: "application/pdf" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${baseName}_extracted_pages.pdf`;
                    a.click();
                    a.remove();
                    showToast(`Extracted ${sortedIndices.length} pages into PDF!`, "success");
                }
            } catch (err) {
                console.error("Split Error:", err);
                showToast("Failed to split PDF: " + err.message, "error");
            }
        });
    }

    // Tool 5: Rotate PDF
    const rDrop = document.getElementById('rotate-drop-zone');
    const rInput = document.getElementById('rotate-file-input');
    const rActionBar = document.getElementById('rotate-action-bar');
    const rStatus = document.getElementById('rotate-status-text');
    const selRotateAngle = document.getElementById('sel-rotate-angle');
    const btnExecRotate = document.getElementById('btn-execute-rotate');

    let loadedRotateFile = null;
    let loadedRotateBytes = null;

    if (rDrop && rInput) {
        rDrop.addEventListener('click', () => rInput.click());
        rDrop.addEventListener('dragover', (e) => { e.preventDefault(); rDrop.classList.add('dragover'); });
        rDrop.addEventListener('dragleave', () => rDrop.classList.remove('dragover'));
        rDrop.addEventListener('drop', (e) => {
            e.preventDefault();
            rDrop.classList.remove('dragover');
            if (e.dataTransfer.files.length) handleRotateDoc(e.dataTransfer.files[0]);
        });
        rInput.addEventListener('change', (e) => {
            if (e.target.files.length) handleRotateDoc(e.target.files[0]);
        });
    }

    async function handleRotateDoc(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            return showToast("Please select a PDF document.", "error");
        }
        try {
            loadedRotateBytes = await file.arrayBuffer();
            const srcDoc = await PDFLib.PDFDocument.load(loadedRotateBytes);
            loadedRotateFile = file;
            rActionBar.style.display = 'flex';
            rStatus.innerText = `${file.name} • ${srcDoc.getPageCount()} pages`;
            showToast(`Loaded ${file.name} (${srcDoc.getPageCount()} pages)`, "success");
        } catch (err) {
            console.error("PDF Load Error:", err);
            showToast("Failed to load PDF: " + err.message, "error");
        }
    }

    if (btnExecRotate) {
        btnExecRotate.addEventListener('click', async () => {
            if (!loadedRotateFile || !loadedRotateBytes) return showToast("Please select a PDF to rotate first.", "error");
            showToast("Rotating PDF in browser memory...", "success");
            try {
                const pdfDoc = await PDFLib.PDFDocument.load(loadedRotateBytes);
                const angle = parseInt(selRotateAngle.value, 10) || 90;
                const pages = pdfDoc.getPages();
                pages.forEach(page => {
                    const currentRotation = page.getRotation().angle;
                    page.setRotation(PDFLib.degrees((currentRotation + angle) % 360));
                });

                const rotatedBytes = await pdfDoc.save();
                const blob = new Blob([rotatedBytes], { type: "application/pdf" });
                const url = URL.createObjectURL(blob);
                const baseName = loadedRotateFile.name.replace(/\.pdf$/i, '');
                const a = document.createElement('a');
                a.href = url;
                a.download = `${baseName}_rotated.pdf`;
                a.click();
                a.remove();
                showToast(`PDF rotated (${angle}°) and downloaded!`, "success");
            } catch (err) {
                console.error("Rotate Error:", err);
                showToast("Failed to rotate PDF: " + err.message, "error");
            }
        });
    }

    // Tool 6: Extract Text from PDF
    const eDrop = document.getElementById('extract-drop-zone');
    const eInput = document.getElementById('extract-file-input');
    const eActionBar = document.getElementById('extract-action-bar');
    const eStatus = document.getElementById('extract-status-text');
    const eWrapper = document.getElementById('extract-viewer-wrapper');
    const txtExtracted = document.getElementById('txt-extracted-content');
    const btnCopyExtracted = document.getElementById('btn-copy-extracted');
    const btnDownloadExtracted = document.getElementById('btn-download-extracted');
    const btnOpenExtractedInStudio = document.getElementById('btn-open-extracted-in-studio');

    let currentExtractedText = "";
    let extractedDocName = "document";

    if (eDrop && eInput) {
        eDrop.addEventListener('click', () => eInput.click());
        eDrop.addEventListener('dragover', (e) => { e.preventDefault(); eDrop.classList.add('dragover'); });
        eDrop.addEventListener('dragleave', () => eDrop.classList.remove('dragover'));
        eDrop.addEventListener('drop', (e) => {
            e.preventDefault();
            eDrop.classList.remove('dragover');
            if (e.dataTransfer.files.length) handleExtractDoc(e.dataTransfer.files[0]);
        });
        eInput.addEventListener('change', (e) => {
            if (e.target.files.length) handleExtractDoc(e.target.files[0]);
        });
    }

    async function handleExtractDoc(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            return showToast("Please select a PDF document.", "error");
        }
        showToast("Extracting text locally in browser...", "success");
        extractedDocName = file.name.replace(/\.pdf$/i, '');
        try {
            const arrayBuffer = await file.arrayBuffer();
            const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
            const pdfDoc = await loadingTask.promise;

            const textChunks = [];
            for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
                const page = await pdfDoc.getPage(pageNum);
                const content = await page.getTextContent();
                const strings = content.items.map(item => item.str).join(' ');
                textChunks.push(`<!-- Page ${pageNum} of ${pdfDoc.numPages} -->\n${strings.trim()}\n`);
            }

            currentExtractedText = textChunks.join('\n').trim();
            txtExtracted.value = currentExtractedText;
            eActionBar.style.display = 'flex';
            eWrapper.style.display = 'block';

            const words = currentExtractedText ? currentExtractedText.split(/\s+/).length : 0;
            eStatus.innerText = `${file.name} • ${words.toLocaleString()} words extracted (${pdfDoc.numPages} pages)`;
            showToast(`Extracted ${words.toLocaleString()} words successfully!`, "success");
        } catch (err) {
            console.error("Text Extract Error:", err);
            showToast("Failed to extract text: " + err.message, "error");
        }
    }

    if (btnCopyExtracted) {
        btnCopyExtracted.addEventListener('click', async () => {
            if (!currentExtractedText) return showToast("No text to copy.", "error");
            try {
                await navigator.clipboard.writeText(currentExtractedText);
                showToast("Text copied to clipboard!", "success");
            } catch (err) {
                txtExtracted.select();
                document.execCommand('copy');
                showToast("Text copied to clipboard!", "success");
            }
        });
    }

    if (btnDownloadExtracted) {
        btnDownloadExtracted.addEventListener('click', () => {
            if (!currentExtractedText) return showToast("No text to download.", "error");
            const blob = new Blob([currentExtractedText], { type: "text/markdown;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${extractedDocName}_extracted.md`;
            a.click();
            a.remove();
            showToast(`Saved "${extractedDocName}_extracted.md"!`, "success");
        });
    }

    if (btnOpenExtractedInStudio) {
        btnOpenExtractedInStudio.addEventListener('click', () => {
            if (!currentExtractedText) return showToast('Extract text from a PDF first.', 'error');
            loadMarkdownDocument(currentExtractedText);
            document.getElementById('btn-mode-markdown').click();
            showToast('PDF text opened in the Markdown editor.', 'success');
        });
    }
}

