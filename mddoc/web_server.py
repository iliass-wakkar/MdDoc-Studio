"""
MdDoc Web Studio — Offline Local Web Interface.
Runs an embedded HTTP server and opens directly in the default browser with zero terminal window.
"""

import os
import sys
import json
import socket
import urllib.parse
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional

# Ensure repo root is on sys.path for direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from .themes import THEMES, get_theme
    from .native_converter import parse_frontmatter, MarkdownToDocxConverter
    from .pandoc_converter import convert_with_pandoc, is_pandoc_available
except (ImportError, ValueError):
    from mddoc.themes import THEMES, get_theme
    from mddoc.native_converter import parse_frontmatter, MarkdownToDocxConverter
    from mddoc.pandoc_converter import convert_with_pandoc, is_pandoc_available


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MdDoc — Markdown to Beautiful DOCX Studio</title>
    <style>
        :root {
            --primary: #1E3A5F;
            --primary-hover: #2E5A7E;
            --secondary: #2E8B8B;
            --bg: #F8FAFC;
            --card-bg: #FFFFFF;
            --text: #1E293B;
            --text-muted: #64748B;
            --border: #E2E8F0;
            --radius: 10px;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: var(--bg); color: var(--text); line-height: 1.5; padding: 24px; }
        .container { max-width: 1100px; margin: 0 auto; }
        
        /* Header */
        header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
        .brand { display: flex; align-items: center; gap: 12px; }
        .brand-logo { width: 42px; height: 42px; background: linear-gradient(135deg, #1E3A5F, #2E8B8B); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-size: 22px; font-weight: bold; }
        .brand-title { font-size: 22px; font-weight: 700; color: var(--primary); }
        .brand-desc { font-size: 13px; color: var(--text-muted); }

        /* Main Grid */
        .grid { display: grid; grid-template-columns: 1fr 340px; gap: 24px; }
        @media (max-width: 860px) { .grid { grid-template-columns: 1fr; } }

        /* Card */
        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow); margin-bottom: 20px; }
        .card-title { font-size: 15px; font-weight: 600; color: var(--primary); margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }

        /* Drop Zone */
        .drop-zone { border: 2px dashed var(--border); border-radius: 8px; padding: 24px; text-align: center; cursor: pointer; transition: all 0.2s; background: #FAFBFD; }
        .drop-zone:hover, .drop-zone.dragover { border-color: var(--secondary); background: #F0FDF4; }
        .drop-icon { font-size: 32px; color: var(--secondary); margin-bottom: 8px; }

        /* Textarea Editor */
        .editor-container { margin-top: 14px; }
        textarea { width: 100%; height: 380px; padding: 14px; border: 1px solid var(--border); border-radius: 8px; font-family: "Consolas", monospace; font-size: 13px; resize: vertical; line-height: 1.45; background: #FCFDFE; color: #0F172A; }
        textarea:focus { outline: none; border-color: var(--secondary); box-shadow: 0 0 0 3px rgba(46, 139, 139, 0.15); }

        /* Form Inputs */
        .form-group { margin-bottom: 14px; }
        .form-label { display: block; font-size: 12px; font-weight: 600; color: var(--text-muted); margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px; }
        .form-control { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; }
        .form-control:focus { outline: none; border-color: var(--secondary); }

        /* Theme Cards */
        .theme-options { display: flex; flex-direction: column; gap: 8px; }
        .theme-card { border: 1.5px solid var(--border); border-radius: 8px; padding: 10px 12px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; transition: all 0.15s; }
        .theme-card:hover { border-color: var(--secondary); }
        .theme-card.active { border-color: var(--primary); background: #F1F5F9; font-weight: 600; }
        .theme-swatches { display: flex; gap: 4px; }
        .swatch { width: 16px; height: 16px; border-radius: 50%; border: 1px solid rgba(0,0,0,0.1); }

        /* Checkbox Switch */
        .switch-row { display: flex; align-items: center; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #F1F5F9; font-size: 13.5px; }
        .switch-row:last-child { border-bottom: none; }

        /* Convert Button */
        .btn-convert { width: 100%; background: linear-gradient(135deg, #1E3A5F, #2E8B8B); color: white; border: none; border-radius: 8px; padding: 14px; font-size: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 10px rgba(30, 58, 95, 0.25); transition: all 0.2s; }
        .btn-convert:hover { transform: translateY(-1px); box-shadow: 0 6px 14px rgba(30, 58, 95, 0.35); }
        .btn-convert:active { transform: translateY(0); }
        .btn-convert:disabled { background: #94A3B8; cursor: not-allowed; transform: none; box-shadow: none; }

        /* Status Toast */
        #status-box { margin-top: 14px; padding: 12px; border-radius: 8px; font-size: 13.5px; display: none; text-align: center; }
        .status-success { background: #DCFCE7; color: #166534; border: 1px solid #BBF7D0; }
        .status-error { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <div class="brand-logo">📄</div>
                <div>
                    <div class="brand-title">MdDoc Studio</div>
                    <div class="brand-desc">Markdown to Publication-Quality Word Document Generator</div>
                </div>
            </div>
            <div style="font-size: 12px; color: var(--text-muted);">100% Offline • Zero Cloud • Local Processing</div>
        </header>

        <div class="grid">
            <!-- Left: Markdown Input & Editor -->
            <div>
                <div class="card">
                    <div class="card-title"><span>📝</span> Markdown Content</div>
                    
                    <div class="drop-zone" id="drop-zone">
                        <div class="drop-icon">📂</div>
                        <div style="font-weight: 600; margin-bottom: 2px;">Drag & Drop your .md file here</div>
                        <div style="font-size: 12px; color: var(--text-muted);">or click to browse from your computer</div>
                        <input type="file" id="file-input" accept=".md,.markdown,.txt" style="display: none;">
                    </div>

                    <div class="editor-container">
                        <textarea id="md-editor" placeholder="Write or paste your Markdown here...

# Document Title

> [!NOTE]
> This is a callout box.

| Feature | Status |
|---|---|
| Offline Engine | Enabled |
"></textarea>
                    </div>
                </div>
            </div>

            <!-- Right: Settings & Actions -->
            <div>
                <div class="card">
                    <div class="card-title"><span>🎨</span> Design Theme</div>
                    <div class="theme-options">
                        <div class="theme-card active" data-theme="modern">
                            <div><strong>Modern Tech</strong><div style="font-size: 11px; color: var(--text-muted);">Cambria • Navy & Teal</div></div>
                            <div class="theme-swatches"><div class="swatch" style="background:#1E3A5F;"></div><div class="swatch" style="background:#2E8B8B;"></div><div class="swatch" style="background:#E07A5F;"></div></div>
                        </div>
                        <div class="theme-card" data-theme="nordic">
                            <div><strong>Nordic Minimal</strong><div style="font-size: 11px; color: var(--text-muted);">Segoe UI • Charcoal & Blue</div></div>
                            <div class="theme-swatches"><div class="swatch" style="background:#2E3440;"></div><div class="swatch" style="background:#5E81AC;"></div><div class="swatch" style="background:#BF616A;"></div></div>
                        </div>
                        <div class="theme-card" data-theme="academic">
                            <div><strong>Academic Classic</strong><div style="font-size: 11px; color: var(--text-muted);">Georgia • Oxford & Amber</div></div>
                            <div class="theme-swatches"><div class="swatch" style="background:#1A365D;"></div><div class="swatch" style="background:#744210;"></div><div class="swatch" style="background:#C05621;"></div></div>
                        </div>
                        <div class="theme-card" data-theme="forest">
                            <div><strong>Forest Moss</strong><div style="font-size: 11px; color: var(--text-muted);">Cambria • Green & Ochre</div></div>
                            <div class="theme-swatches"><div class="swatch" style="background:#1C4532;"></div><div class="swatch" style="background:#2F855A;"></div><div class="swatch" style="background:#D69E2E;"></div></div>
                        </div>
                        <div class="theme-card" data-theme="corporate">
                            <div><strong>Corporate Blue</strong><div style="font-size: 11px; color: var(--text-muted);">Arial • Executive Navy</div></div>
                            <div class="theme-swatches"><div class="swatch" style="background:#0F2942;"></div><div class="swatch" style="background:#1E6091;"></div><div class="swatch" style="background:#00A896;"></div></div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title"><span>⚙️</span> Document Settings</div>
                    
                    <div class="switch-row">
                        <span>Cover Page</span>
                        <input type="checkbox" id="chk-cover" checked>
                    </div>
                    <div class="switch-row">
                        <span>Table of Contents</span>
                        <input type="checkbox" id="chk-toc" checked>
                    </div>
                    
                    <div class="form-group" style="margin-top: 12px;">
                        <label class="form-label">Page Size</label>
                        <select id="sel-pagesize" class="form-control">
                            <option value="A4" selected>A4 (Standard)</option>
                            <option value="Letter">US Letter</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Document Title (Optional)</label>
                        <input type="text" id="inp-title" class="form-control" placeholder="Auto-detected from Markdown">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Author (Optional)</label>
                        <input type="text" id="inp-author" class="form-control" placeholder="e.g. John Doe">
                    </div>
                </div>

                <button class="btn-convert" id="btn-convert">
                    <span>✨ Generate & Download DOCX</span>
                </button>

                <div id="status-box"></div>
            </div>
        </div>
    </div>

    <script>
        let selectedTheme = "modern";

        // Theme selection
        document.querySelectorAll('.theme-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.theme-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                selectedTheme = card.dataset.theme;
            });
        });

        // File drop & browse
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const mdEditor = document.getElementById('md-editor');

        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
        });
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) handleFile(e.target.files[0]);
        });

        function handleFile(file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                mdEditor.value = e.target.result;
                showStatus(`Loaded file: ${file.name}`, 'status-success');
            };
            reader.readAsText(file);
        }

        // Convert Button Click
        const btnConvert = document.getElementById('btn-convert');
        const statusBox = document.getElementById('status-box');

        btnConvert.addEventListener('click', async () => {
            const mdContent = mdEditor.value.trim();
            if (!mdContent) {
                showStatus("Please write or upload some Markdown content first.", "status-error");
                return;
            }

            btnConvert.disabled = true;
            btnConvert.innerHTML = "<span>⏳ Generating DOCX...</span>";
            showStatus("Converting document...", "status-success");

            const payload = {
                markdown: mdContent,
                theme: selectedTheme,
                title: document.getElementById('inp-title').value.trim() || null,
                author: document.getElementById('inp-author').value.trim() || null,
                cover_page: document.getElementById('chk-cover').checked,
                toc: document.getElementById('chk-toc').checked,
                page_size: document.getElementById('sel-pagesize').value
            };

            try {
                const response = await fetch('/api/convert', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const errData = await response.json();
                    throw new Error(errData.error || "Conversion failed");
                }

                // Download blob
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = (payload.title ? payload.title.replace(/[^a-zA-Z0-9_-]/g, '_') : 'document') + '.docx';
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);

                showStatus("✔ DOCX generated and downloaded successfully!", "status-success");
            } catch (err) {
                showStatus(`❌ Error: ${err.message}`, "status-error");
            } finally {
                btnConvert.disabled = false;
                btnConvert.innerHTML = "<span>✨ Generate & Download DOCX</span>";
            }
        });

        function showStatus(msg, className) {
            statusBox.style.display = 'block';
            statusBox.className = className;
            statusBox.innerText = msg;
        }
    </script>
</body>
</html>
"""


class MdDocRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/convert":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(body)
                md_text = data.get("markdown", "")
                theme_name = data.get("theme", "modern")
                title = data.get("title")
                author = data.get("author")
                show_cover = data.get("cover_page", True)
                show_toc = data.get("toc", True)
                page_size = data.get("page_size", "A4")

                converter = MarkdownToDocxConverter(
                    theme_name=theme_name,
                    title=title,
                    author=author,
                    show_cover=show_cover,
                    show_toc=show_toc,
                    page_size=page_size
                )
                doc = converter.convert(md_text)

                import io
                bio = io.BytesIO()
                doc.save(bio)
                docx_bytes = bio.getvalue()

                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                self.send_header("Content-Disposition", 'attachment; filename="document.docx"')
                self.send_header("Content-Length", str(len(docx_bytes)))
                self.end_headers()
                self.wfile.write(docx_bytes)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress console log spam


def find_free_port(start_port=8765):
    """Find an available port."""
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port


def launch_web_ui(port=None):
    """Launch embedded HTTP server and open browser window."""
    if port is None:
        port = find_free_port(8765)

    server = HTTPServer(('127.0.0.1', port), MdDocRequestHandler)
    url = f"http://127.0.0.1:{port}"
    
    # Open browser automatically
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    
    print(f"[*] MdDoc Web Studio running at: {url}")
    print("[*] Press Ctrl+C to stop server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("\n[*] Server stopped.")


if __name__ == "__main__":
    launch_web_ui()
