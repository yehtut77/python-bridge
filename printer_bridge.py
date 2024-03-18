import tkinter as tk
from tkinter import ttk
import win32print
import win32api
import tempfile
import threading
import http.server
import socketserver
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

# Function to get available printers
def get_printers():
    printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
    return printers

# Function to print a test receipt
def print_test_receipt(printer_name):
    # Preparing a simple text file to print
    filename = tempfile.mktemp(suffix=".txt")
    with open(filename, "w") as f:
        f.write("***** POS RECEIPT *****\n\n")
        f.write("Item A: $5.00\n")
        f.write("Item B: $3.50\n")
        f.write("\nThank You!\n")
    # Printing the file
    win32api.ShellExecute(0, "print", filename, f'/d:"{printer_name}"', ".", 0)

# Your existing GUI setup here...
app = tk.Tk()
app.title("Printer Bridge with win32print and HTTP Server")
app.geometry("400x200")

printer_label = ttk.Label(app, text="Select Printer:")
printer_label.pack(pady=5)

printer_combo = ttk.Combobox(app, values=get_printers())
printer_combo.pack(pady=5)

print_button = ttk.Button(app, text="Print Test Receipt")
print_button.pack(pady=20)

# HTTP Server Handler
class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = parse_qs(post_data.decode())
        printer_name = printer_combo.get()  # Get the selected printer from the GUI
        
        # Assuming the data sent to the server includes a field named 'action' with the value 'print'
        if data.get('action', [''])[0] == 'print':
            print_test_receipt(printer_name)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response = bytes("Receipt printed successfully.", "utf-8")
            self.wfile.write(response)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response = bytes("Invalid request", "utf-8")
            self.wfile.write(response)

def run_server(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

# Run the server in a separate thread
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

app.mainloop()
