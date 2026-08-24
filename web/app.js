/**
 * MdDoc Studio Application JavaScript.
 * Coordinates UI, Live Preview, and WebAssembly Worker.
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
| **5 Curated Themes** | Modern, Nordic, Academic, Forest, Corporate | Included |
| **Cover Page Generator** | Clean typography & accent geometry | Enabled |
| **Table Formatting** | Booktabs style with zebra striping | Enabled |
| **GFM Admonitions** | Styled note & warning callout boxes | Supported |

## Callout Alerts

> [!NOTE]
> This document was generated entirely in-browser using WebAssembly.

> [!TIP]
> Drag and drop any .md file directly onto this window to convert it instantly!
`;

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
const btnText = document.getElementById('btn-text');
const engineStatus = document.getElementById('engine-status');
const statusText = document.getElementById('status-text');
const statusToast = document.getElementById('status-toast');

// Inputs
const inpTitle = document.getElementById('meta-title');
const inpAuthor = document.getElementById('meta-author');
const inpSubtitle = document.getElementById('meta-subtitle');
const chkCover = document.getElementById('chk-cover');
const chkToc = document.getElementById('chk-toc');
const selPageSize = document.getElementById('sel-pagesize');

// Initialize Worker
function initWorker() {
    worker = new Worker('worker.js?v=' + Date.now());

    worker.onmessage = function (e) {
        const { type, message, data } = e.data;

        if (type === "STATUS") {
            statusText.innerText = message;
        } else if (type === "READY") {
            isEngineReady = true;
            engineStatus.classList.remove('loading');
            engineStatus.classList.add('ready');
            statusText.innerText = "Engine Ready (WASM)";
            btnExport.disabled = false;
        } else if (type === "CONVERT_SUCCESS") {
            onExportSuccess(data);
        } else if (type === "ERROR") {
            onExportError(message);
        }
    };

    worker.onerror = function (err) {
        console.error("Worker Error:", err);
        statusText.innerText = "Engine Error";
        showToast("Engine initialization error: " + err.message, "error");
    };
}

// Theme Styles Specification for Live Preview
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

// Apply CSS Variables to Live Preview
function applyThemeToPreview(themeName) {
    const t = THEME_STYLES[themeName] || THEME_STYLES.modern;
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
    // Strip YAML frontmatter for preview rendering if present
    const cleanMd = raw.replace(/^---\s*[\r\n]+[\s\S]*?[\r\n]+---\s*[\r\n]+/, '');

    let html = "";

    // If cover page toggle is enabled, prepend styled visual cover banner
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
        applyThemeToPreview(themeName);
        updatePreview();
    }
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
    btnExport.addEventListener('click', () => {
        const text = mdInput.value.trim();
        if (!text) {
            showToast("Please enter or upload Markdown content first.", "error");
            return;
        }

        if (!isEngineReady) {
            showToast("Engine is still loading WebAssembly, please wait...", "error");
            return;
        }

        btnExport.disabled = true;
        btnText.innerText = "Generating DOCX in Browser...";
        showToast("Converting document locally...", "success");

        const payload = {
            markdown: text,
            theme: selectedTheme,
            title: inpTitle.value.trim() || null,
            subtitle: inpSubtitle.value.trim() || null,
            author: inpAuthor.value.trim() || null,
            show_cover: chkCover.checked,
            show_toc: chkToc.checked,
            page_size: selPageSize.value
        };

        worker.postMessage({
            action: "CONVERT",
            id: Date.now(),
            payload
        });
    });
}

function onExportSuccess(uint8Array) {
    btnExport.disabled = false;
    btnText.innerText = "Export to Word (.docx)";

    // Create download blob
    const blob = new Blob([uint8Array], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    
    let docName = inpTitle.value.trim() || "document";
    docName = docName.replace(/[^a-zA-Z0-9_\-\s]/g, '').trim().replace(/\s+/g, '_');
    a.download = `${docName || "document"}.docx`;
    
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    showToast("✔ Document converted & downloaded successfully!", "success");
}

function onExportError(errMsg) {
    btnExport.disabled = false;
    btnText.innerText = "Export to Word (.docx)";
    showToast("❌ Conversion failed: " + errMsg, "error");
}

function showToast(msg, type) {
    statusToast.style.display = 'block';
    statusToast.className = `status-toast ${type}`;
    statusToast.innerText = msg;
}

// Event Listeners & Boot
document.addEventListener('DOMContentLoaded', () => {
    initWorker();
    setupTabs();
    setupFileUpload();
    setupExport();

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
        showToast("Loaded comprehensive sample document.", "success");
    });

    // Clear button
    btnClear.addEventListener('click', () => {
        if (confirm("Clear editor content?")) {
            mdInput.value = "";
            updatePreview();
        }
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

    // Load default sample initially
    mdInput.value = SAMPLE_MARKDOWN;
    inpTitle.value = "MdDoc Architecture & Specification";
    inpSubtitle.value = "High-Performance Markdown to Publication-Quality Word DOCX";
    inpAuthor.value = "Engineering Team";
    selectTheme("modern");
    updatePreview();
});
