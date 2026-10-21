"""
Serveur simple pour tester les relais
"""

from http.server import HTTPServer, BaseHTTPRequestHandler

HOST = "127.0.0.1"
PORT = 8000

# Map each URL path to a tiny HTML response
PAGES = {
    "/t1":   "<html><body><h1>Page T1</h1></body></html>",
    "/t2":   "<html><body><h1>Page T2</h1></body></html>",
    "/t3":   "<html><body><h1>Page T3</h1></body></html>",
    "/t4/t41": "<html><body><h1>Page T4/T41</h1></body></html>",
}

class SimpleRouter(BaseHTTPRequestHandler):
    def do_GET(self):
        content = PAGES.get(self.path)
        if content is not None:
            # 200 OK for known routes
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        else:
            # 404 Not Found for everything else
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"404 Not Found")

def run_server():
    server = HTTPServer((HOST, PORT), SimpleRouter)
    print(f"Serving on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()

if __name__ == "__main__":
    run_server()

