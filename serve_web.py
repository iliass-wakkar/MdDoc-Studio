#!/usr/bin/env python3
"""
Dedicated Web Studio Local Server on clean port 8899.
"""

import http.server
import socketserver
import os
import sys
import webbrowser

PORT = 8899
web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=web_dir, **kwargs)
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

class ReuseServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    print(f"[*] Serving MdDoc Web Studio from: {web_dir}")
    url = f"http://localhost:{PORT}"
    print(f"[*] Opening browser: {url}")
    with ReuseServer(('127.0.0.1', PORT), CustomHandler) as httpd:
        webbrowser.open(url)
        httpd.serve_forever()
