import http.server
import socketserver
import os
import sys

# Import centralized ecosystem port registry if available
sys.path.insert(0, r"c:\KIRTSOY_CORE\AI_PROGRAMS\AI MAXXING")
try:
    from port_registry import acquire_port
    PORT = acquire_port("LOGO Studio", fallback_range=(8590, 8620))
except Exception as e:
    PORT = 8590

DIRECTORY = r"c:\KIRTSOY_CORE\AI_PROGRAMS\LOGO"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

if __name__ == '__main__':
    with ThreadingServer(("", PORT), Handler) as httpd:
        print(f"Serving LOGO Studio at http://localhost:{PORT}")
        httpd.serve_forever()
