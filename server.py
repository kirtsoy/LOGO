import http.server
import socketserver
import os
import sys
import json
import glob

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

    def do_POST(self):
        if self.path.startswith('/api/compile_prores'):
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                # Save uploaded ZIP to a temporary file in renders/
                renders_dir = os.path.join(DIRECTORY, "renders")
                os.makedirs(renders_dir, exist_ok=True)
                temp_zip = os.path.join(renders_dir, f"temp_upload_{os.getpid()}.zip")
                
                with open(temp_zip, "wb") as f:
                    f.write(post_data)
                
                from convert_png_to_video import compile_sequence_to_video
                result = compile_sequence_to_video(temp_zip)
                
                if os.path.exists(temp_zip):
                    try:
                        os.remove(temp_zip)
                    except Exception:
                        pass
                
                if result and result.get("prores_file"):
                    res_body = json.dumps({
                        "status": "ok",
                        "prores_url": f"/renders/{result['prores_file']}",
                        "prores_name": result['prores_file'],
                        "webm_url": f"/renders/{result['webm_file']}" if result.get('webm_file') else None,
                        "frames": result['frames']
                    }).encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(res_body)))
                    self.end_headers()
                    self.wfile.write(res_body)
                else:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    err_msg = json.dumps({"status": "error", "message": "FFmpeg encoding failed"}).encode('utf-8')
                    self.send_header('Content-Length', str(len(err_msg)))
                    self.end_headers()
                    self.wfile.write(err_msg)
            except Exception as e:
                err_msg = json.dumps({"status": "error", "message": str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(err_msg)))
                self.end_headers()
                self.wfile.write(err_msg)
            return

        self.send_error(404, "Endpoint not found")

class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

if __name__ == '__main__':
    with ThreadingServer(("", PORT), Handler) as httpd:
        print(f"Serving LOGO Studio at http://localhost:{PORT}")
        httpd.serve_forever()
