from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import base64
 
RESULT_PATH = "/temp/results.txt"
os.makedirs(os.path.dirname(RESULT_PATH), exist_ok=True)
 
class SumQuoteHandler(BaseHTTPRequestHandler):
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
 
        elif self.path == "/quote":
            # Controllo che il file quote esista
            quote_path = "/dev/attestation/quote"
            att_type_path = "/dev/attestation/attestation_type"
            user_report_data_path = "/dev/attestation/user_report_data"
 
            if not os.path.exists(quote_path):
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Cannot find `/dev/attestation/quote`; SGX attestation not enabled?"}).encode('utf-8'))
                return
 
            try:
                # Scrivo 64 bytes zero nel report data (puoi personalizzare se vuoi)
                with open(user_report_data_path, "wb") as f:
                    f.write(b'\0'*64)
 
                # Leggo il tipo di attestazione
                with open(att_type_path) as f:
                    att_type = f.read().strip()
 
                # Leggo la quote binaria
                with open(quote_path, "rb") as f:
                    quote = f.read()
 
                # Codifico la quote in base64 per trasmissione JSON
                quote_b64 = base64.b64encode(quote).decode('utf-8')
 
                response = {
                    "attestation_type": att_type,
                    "quote_base64": quote_b64,
                    "quote_size": len(quote)
                }
 
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
 
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
 
        else:
            self.send_response(404)
            self.end_headers()
 
def run(server_class=HTTPServer, handler_class=SumQuoteHandler, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving on port {port}...")
    httpd.serve_forever()
 
if __name__ == "__main__":
    run()