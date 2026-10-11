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

    previewContent.innerHTML = html;
    applyThemeToPreview(selectedTheme);
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
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
        }
    });
}

// Theme Selector
function selectTheme(themeName) {
    const target = document.querySelector(`.theme-option[data-theme="${themeName}"]`);
    if (target) {
        document.querySelectorAll('.theme-option').forEach(el => el.classList.remove('active'));
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
                showToast(`Applied "${btn.innerText}" preset!`, "success");
            }
        });
    });
}

// Tab Switching
function setupTabs() {
    tabEditorBtn.addEventListener('click', () => {
        tabEditorBtn.classList.add('active');
        tabPreviewBtn.classList.remove('active');
        editorTabView.classList.add('active');
        previewTabView.classList.remove('active');
    });

    tabPreviewBtn.addEventListener('click', () => {
        tabPreviewBtn.classList.add('active');
        tabEditorBtn.classList.remove('active');
        previewTabView.classList.add('active');
        editorTabView.classList.remove('active');
        updatePreview();
    });
}

// Drag and Drop & File Input
function setupFileUpload() {
    const handleFile = (file) => {
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            mdInput.value = e.target.result;
            checkAndApplyFrontmatter(e.target.result);
            updatePreview();
            showToast(`Loaded "${file.name}"`, "success");
        };
        reader.readAsText(file);
    };

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
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

    if (btnExport) btnExport.addEventListener('click', triggerExport);
    if (btnHeaderExport) btnHeaderExport.addEventListener('click', triggerExport);
    if (btnToolbarExport) btnToolbarExport.addEventListener('click', triggerExport);
    if (btnExportTypst) btnExportTypst.addEventListener('click', triggerTypstExport);
}

function onTypstSuccess(typstSource) {
    if (btnExportTypst) btnExportTypst.disabled = false;
    if (btnTypstText) btnTypstText.innerText = "Export Typst / PDF (.typ)";

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
            <div class="download-box-text">🎉 Word Document Ready!</div>
            <a href="${url}" download="${fileName}">⬇️ Click to Re-Download (${fileName})</a>
        `;
    }

    showToast(`✔ Downloaded "${fileName}" successfully!`, "success");
}

function onExportError(errMsg) {
    if (btnExport) btnExport.disabled = false;
    if (btnHeaderExport) btnHeaderExport.disabled = false;
    if (btnToolbarExport) btnToolbarExport.disabled = false;
    if (btnText) btnText.innerText = "Download Word Document (.docx)";
    showToast("❌ Conversion failed: " + errMsg, "error");
}

function showToast(msg, type) {
    statusToast.style.display = 'block';
    statusToast.className = `status-toast ${type}`;
    statusToast.innerText = msg;
}

// In-App Modal Dialog
function showModal({ icon = "⚠️", title = "Confirmation", message = "", confirmText = "Confirm", isDanger = false, onConfirm }) {
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
    
    modal.style.display = 'flex';
    
    const closeModal = () => {
        modal.style.display = 'none';
        mConfirm.onclick = null;
        mCancel.onclick = null;
    };
    
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

    // Theme card clicks
    document.querySelectorAll('.theme-option').forEach(card => {
        card.addEventListener('click', () => {
            selectTheme(card.dataset.theme);
        });
    });

    // Sample button
    btnSample.addEventListener('click', () => {
        mdInput.value = SAMPLE_MARKDOWN;
        inpTitle.value = "MdDoc Architecture & Specification";
        inpSubtitle.value = "High-Performance Markdown to Publication-Quality Word DOCX";
        inpAuthor.value = "Engineering Team";
        selectTheme("modern");
        updatePreview();
        showToast("Loaded sample document.", "success");
    });

    // Clear button with In-App Modal Dialog
    btnClear.addEventListener('click', () => {
        showModal({
            icon: "🗑️",
            title: "Clear Editor Content?",
            message: "Are you sure you want to clear all Markdown content? This action cannot be undone.",
            confirmText: "Yes, Clear All",
            isDanger: true,
            onConfirm: () => {
                mdInput.value = "";
                updatePreview();
                showToast("Editor content cleared.", "success");
            }
        });
    });

    // Auto-update preview on typing (debounced)
    let debounceTimer = null;
    mdInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(updatePreview, 300);
    });

    // Auto-update preview when metadata or toggles change
    [inpTitle, inpSubtitle, inpAuthor].forEach(el => {
        el.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(updatePreview, 150);
        });
    });
    chkCover.addEventListener('change', updatePreview);

    // Multi-Mode Studio Setups
    setupStudioNavigation();
    setupDocxConverter();
    setupPdfToolbox();

    // Initial setup
    updateCustomSwatches();
    mdInput.value = SAMPLE_MARKDOWN;
    inpTitle.value = "MdDoc Architecture & Specification";
    inpSubtitle.value = "High-Performance Markdown to Publication-Quality Word DOCX";
    inpAuthor.value = "Engineering Team";
    selectTheme("modern");
    updatePreview();
});

// ==========================================================================
// STUDIO MODE NAVIGATION
// ==========================================================================
function setupStudioNavigation() {
    const btnModeMd = document.getElementById('btn-mode-markdown');
    const btnModeDocx = document.getElementById('btn-mode-docx');
    const btnModePdf = document.getElementById('btn-mode-pdf');

    const viewMd = document.getElementById('view-mode-markdown');
    const viewDocx = document.getElementById('view-mode-docx');
    const viewPdf = document.getElementById('view-mode-pdf');

    const switchMode = (mode) => {
        [btnModeMd, btnModeDocx, btnModePdf].forEach(b => b && b.classList.remove('active'));
        [viewMd, viewDocx, viewPdf].forEach(v => v && (v.style.display = 'none'));

        if (mode === 'markdown') {
            if (btnModeMd) btnModeMd.classList.add('active');
            if (viewMd) viewMd.style.display = 'block';
        } else if (mode === 'docx') {
            if (btnModeDocx) btnModeDocx.classList.add('active');
            if (viewDocx) viewDocx.style.display = 'block';
        } else if (mode === 'pdf') {
            if (btnModePdf) btnModePdf.classList.add('active');
            if (viewPdf) viewPdf.style.display = 'block';
        }
    };

    if (btnModeMd) btnModeMd.addEventListener('click', () => switchMode('markdown'));
    if (btnModeDocx) btnModeDocx.addEventListener('click', () => switchMode('docx'));
    if (btnModePdf) btnModePdf.addEventListener('click', () => switchMode('pdf'));
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
    const btnOpenInStudio = document.getElementById('btn-open-in-studio');

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
    });

    const handleDocxFile = async (file) => {
        if (!file.name.toLowerCase().endsWith('.docx')) {
            showToast("Please select a valid Microsoft Word (.docx) document.", "error");
            return;
        }

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

    if (btnOpenInStudio) {
        btnOpenInStudio.addEventListener('click', () => {
            const text = outputArea.value.trim();
            if (!text) return showToast("No Markdown to load into Studio.", "error");
            mdInput.value = text;
            checkAndApplyFrontmatter(text);
            updatePreview();
            document.getElementById('btn-mode-markdown').click();
            showToast("Document opened in Markdown Studio!", "success");
        });
    }
}

// ==========================================================================
// CLIENT-SIDE PDF TOOLBOX (PDF.JS, PDF-LIB, JSZIP)
// ==========================================================================
function setupPdfToolbox() {
    // Subtabs
    const subtabs = document.querySelectorAll('.pdf-subtab-btn');
    subtabs.forEach(btn => {
        btn.addEventListener('click', () => {
            subtabs.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const sub = btn.dataset.sub;
            document.querySelectorAll('.pdf-panel-content').forEach(p => p.style.display = 'none');
            const target = document.getElementById(`pdf-panel-${sub}`);
            if (target) target.style.display = 'block';
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
                        <button class="btn-thumb-download" data-page="${pageNum}">⬇️ Save PNG</button>
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
    const btnCompilePdf = document.getElementById('btn-compile-images-pdf');

    let loadedImages = [];

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
        });
    }

    function handleLoadedImages(files) {
        const valid = files.filter(f => f.type.startsWith('image/'));
        if (!valid.length) return showToast("Please select valid image files.", "error");
        loadedImages.push(...valid);
        i2pActionBar.style.display = 'flex';
        i2pStatus.innerText = `${loadedImages.length} images queued`;
        renderImagesList();
        showToast(`Added ${valid.length} images!`, "success");
    }

    function renderImagesList() {
        i2pGrid.innerHTML = "";
        loadedImages.forEach((img, idx) => {
            const item = document.createElement('div');
            item.className = 'queue-item';
            item.innerHTML = `
                <span>🖼️ Image ${idx + 1}: <strong>${img.name}</strong> (${(img.size / 1024).toFixed(1)} KB)</span>
                <button class="action-btn" style="color:#EF4444;" data-idx="${idx}">✕ Remove</button>
            `;
            item.querySelector('button').onclick = () => {
                loadedImages.splice(idx, 1);
                renderImagesList();
                i2pStatus.innerText = `${loadedImages.length} images queued`;
            };
            i2pGrid.appendChild(item);
        });
    }

    if (btnCompilePdf) {
        btnCompilePdf.addEventListener('click', async () => {
            if (!loadedImages.length) return showToast("Please add images first.", "error");
            showToast("Compiling PDF in browser memory...", "success");
            try {
                const pdfDoc = await PDFLib.PDFDocument.create();
                for (const imgFile of loadedImages) {
                    const bytes = await imgFile.arrayBuffer();
                    let embedded;
                    if (imgFile.type.includes('png')) {
                        embedded = await pdfDoc.embedPng(bytes);
                    } else {
                        embedded = await pdfDoc.embedJpg(bytes);
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
            li.innerHTML = `
                <span>📄 Document ${idx + 1}: <strong>${pdf.name}</strong> (${(pdf.size / 1024).toFixed(1)} KB)</span>
                <button class="action-btn" style="color:#EF4444;" data-idx="${idx}">✕ Remove</button>
            `;
            li.querySelector('button').onclick = () => {
                pdfFilesToMerge.splice(idx, 1);
                renderMergeQueue();
                mStatus.innerText = `${pdfFilesToMerge.length} PDFs queued`;
            };
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
}
