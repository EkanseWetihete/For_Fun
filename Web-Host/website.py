from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from cgi import FieldStorage
import os
from urllib.parse import quote

UPLOAD_DIRECTORY = "uploads"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, content_type="text/html"):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        print(f"Handling GET request from {self.client_address}")
    
        
        if self.path == '/':
            self.path = '/upload.html'
    
        # Handles static files like CSS or JS
        if self.path.endswith('.css'):
            content_type = 'text/css'
        elif self.path.endswith('.js'):
            content_type = 'application/javascript'
        elif self.path.endswith('.html'):
            content_type = 'text/html'
        else:
            content_type = 'application/octet-stream' 
    
        try:
            if self.path == '/upload.html':
                with open('upload.html', 'r') as file:
                    html_content = file.read()
    
                # Gets a list of files from Server Data and modifies HTML file
                file_list_html = self.generate_file_list_html()
                html_content = html_content.replace('<!-- FILE_LIST -->', file_list_html)
    
                # Sends back the modified HTML with a file list
                self._set_headers()
                self.wfile.write(html_content.encode('utf-8'))
                return
    
            file_path = self.path.lstrip('/') 
            with open(file_path, 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except IOError:
            self.send_error(404, "File Not Found")

    def generate_file_list_html(self):
        # Generates a list the files in the upload directory
        try:
            files = os.listdir(UPLOAD_DIRECTORY)
        except FileNotFoundError:
            files = []
        file_list_html = ''
        for filename in files:
            file_list_html += f'<option value="{filename}">{filename}</option>'
        return file_list_html

    def do_POST(self):
        print(f"Handling POST request from {self.client_address}")
        if self.path == '/upload':
            content_type = self.headers['Content-Type']
            if 'multipart/form-data' in content_type:
                form = FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                file_field = form['file']
                if file_field.filename:
                    try:
                        filename = file_field.filename.encode('latin-1').decode('utf-8')
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        filename = file_field.filename

                    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
                    with open(file_path, 'wb') as output_file:
                        output_file.write(file_field.file.read())
                    
                    # Redirects user to refresh the page after successful upload
                    self.send_response(303)  # 303 See Other: Redirect to another URL
                    self.send_header('Location', '/')  # Redirects to the root page
                    self.end_headers()
                    return
                else:
                    self.send_error(400, "No file uploaded")
            else:
                self.send_error(400, "Content-Type not supported")
        elif self.path == '/download':
            content_type = self.headers['Content-Type']
            if 'multipart/form-data' in content_type:
                form = FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                file_field = form['files']
                file_path = os.path.join(UPLOAD_DIRECTORY, file_field.value)
                if os.path.isfile(file_path):
                    print(f"Found file {file_field.value}, preparing to send it to the client.")
                    self.send_response(200)
                    # URL encode the filename
                    encoded_filename = quote(file_field.value)
                    self.send_header('Content-Disposition', f'attachment; filename="{encoded_filename}"')
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.end_headers()
                    with open(file_path, 'rb') as file:
                        self.wfile.write(file.read())
                else:
                    print(f"File {file_field.value} not found.")
                    self.send_error(404, "File Not Found")
            else:
                print("Unsupported Content-Type")
                self.send_error(400, "Content-Type not supported")
        else:
            print("Unknown POST path")
            self.send_error(404, "Not Found")


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    server_address = ('0.0.0.0', 8000)
    httpd = ThreadedHTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Serving on port 8000")
    httpd.serve_forever()
