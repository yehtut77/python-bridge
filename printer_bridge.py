import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading
import tkinter as tk
from tkinter import ttk
import win32print
import win32api
import tempfile

def get_printers():
    printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
    return printers

def print_test_receipt(printer_name, receipt_text):
    filename = tempfile.mktemp(suffix=".txt")
    with open(filename, "w") as f:
        f.write(receipt_text)
    # Printing the file
    win32api.ShellExecute(0, "print", filename, f'/d:"{printer_name}"', ".", 0)

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            printer_name = printer_combo.get()  # Ensure you've selected a printer in the GUI

            # Make sure to check both 'action' is present and its value is 'print'
            if 'action' in data and data['action'] == 'print':
                # Use get to provide a default receipt text if 'text' key is missing
                receipt_text = data.get('text', 'Default Receipt Text')
                print_test_receipt(printer_name, receipt_text)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = json.dumps({"status": "success", "message": "Receipt printed successfully."}).encode()
                self.wfile.write(response)
            else:
                self.send_error(400, "Invalid action value")
        except json.JSONDecodeError:
            self.send_error(400, "Bad Request: Could not decode JSON")

def run_server(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

# GUI Setup
app = tk.Tk()
app.title("Printer Bridge with win32print and HTTP Server")
app.geometry("400x200")

printer_label = ttk.Label(app, text="Select Printer:")
printer_label.pack(pady=5)

printer_combo = ttk.Combobox(app, values=get_printers())
printer_combo.pack(pady=5)

# No need for a print button in this version since printing is triggered by HTTP requests

# Start the server in a separate thread to keep the GUI responsive
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

app.mainloop()
