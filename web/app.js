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

// Live Markdown Preview Update
function updatePreview() {
    const raw = mdInput.value;
    // Strip YAML frontmatter for preview rendering if present
    const cleanMd = raw.replace(/^---\s*[\r\n]+[\s\S]*?[\r\n]+---\s*[\r\n]+/, '');
    if (window.marked) {
        previewContent.innerHTML = marked.parse(cleanMd);
    }
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

    // Load default sample initially
    mdInput.value = SAMPLE_MARKDOWN;
    inpTitle.value = "MdDoc Architecture & Specification";
    inpSubtitle.value = "High-Performance Markdown to Publication-Quality Word DOCX";
    inpAuthor.value = "Engineering Team";
    updatePreview();
});
