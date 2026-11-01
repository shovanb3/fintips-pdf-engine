from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from weasyprint import HTML

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # URL থেকে প্যারামিটার রিড করা (?url=...)
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)
        target_url = params.get('url', [None])[0]

        if not target_url:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Error: URL query parameter is required.")
            return

        try:
            # সরাসরি HTML URL থেকে ভেক্টর PDF জেনারেট (১-২ সেকেন্ডে হবে)
            pdf_bytes = HTML(url=target_url).write_pdf()

            # ব্রাউজারে সরাসরি PDF ডাউনলোড করানোর হেডার
            self.send_response(200)
            self.send_header('Content-type', 'application/pdf')
            self.send_header('Content-Disposition', 'attachment; filename="bulletin.pdf"')
            self.end_headers()
            self.wfile.write(pdf_bytes)

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"PDF Generation Error: {str(e)}".encode())