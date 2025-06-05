from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import base64
import logging

# Configura logging
LOG_FILE = "/var/log/server.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
)
logger = logging.getLogger(__name__)

RESULT_PATH = "/temp/results.txt"
os.makedirs(os.path.dirname(RESULT_PATH), exist_ok=True)

class SumQuoteHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override log HTTP requests
        logger.info("%s - - [%s] %s" % (self.client_address[0],
                                        self.log_date_time_string(),
                                        format % args))

    def do_POST(self):
        logger.info(f"Received POST request on path: {self.path}")

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
                logger.info(f"Result written to {RESULT_PATH}: {result}")

                logger.info(f"Computed sum: {A} + {B} = {result}")

                response = {"A": A, "B": B, "sum": result}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))

            except Exception as e:
                logger.error(f"Error in /sum: {str(e)}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))


        elif self.path == "/quote":
            quote_path = "/dev/attestation/quote"
            att_type_path = "/dev/attestation/attestation_type"
            user_report_data_path = "/dev/attestation/user_report_data"

            if not os.path.exists(quote_path):
                logger.error("Missing /dev/attestation/quote")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Cannot find `/dev/attestation/quote`; SGX attestation not enabled?"}).encode('utf-8'))
                return

            try:
                with open(user_report_data_path, "wb") as f:
                    f.write(b'\0'*64)
                
                with open(att_type_path) as f:
                    att_type = f.read().strip()

                with open(quote_path, "rb") as f:
                    quote = f.read()

                quote_b64 = base64.b64encode(quote).decode('utf-8')

                logger.info(f"Generated attestation quote: type={att_type}, size={len(quote)} bytes")


                response = {
                    "attestation_type": att_type,
                    "quote_base64": quote_b64,
                    "quote_size": len(quote)
                }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')


                self.wfile.write(json.dumps(response).encode('utf-8'))

            except Exception as e:
                logger.error(f"Error in /quote: {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

            else:
                logger.warning(f"404 - Unknown path: {self.path}")
                self.send_response(404)
                self.end_headers()

def run(server_class=HTTPServer, handler_class=SumQuoteHandler, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logger.info(f"HTTP server successfully bound to port {port}. Waiting for connections...")

    httpd.serve_forever()

    if __name__ == "__main__":
        run()



            

