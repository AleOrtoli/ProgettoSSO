from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
 
RESULT_PATH = "/temp/results.txt"
os.makedirs(os.path.dirname(RESULT_PATH), exist_ok=True)
 
class SumHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/sum":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
 
            try:
                data = json.loads(body)
                A = int(data.get("A"))
                B = int(data.get("B"))
                result = A + B
 
                with open(RESULT_PATH, "w") as f:
                    f.write(f"{result}\n")

                # Lettura e stampa del contenuto appena scritto
                with open(RESULT_PATH, "r") as f:
                    content = f.read()
                    print(f"Contenuto scritto in {RESULT_PATH}: {content.strip()}", flush=True)
 
                response = {
                    "A": A,
                    "B": B,
                    "sum": result
                }
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
 
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
 
def run(server_class=HTTPServer, handler_class=SumHandler, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving on port {port}...")
    httpd.serve_forever()
 
if __name__ == "__main__":
    run()