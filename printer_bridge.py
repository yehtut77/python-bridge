import ctypes
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import tkinter as tk
from tkinter import ttk
import win32print
import win32api
import tempfile

# Make the application DPI aware to improve appearance on high DPI displays
def make_app_dpi_aware():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 1: System DPI aware, 2: Per monitor DPI aware
    except (AttributeError, Exception):
        pass  # This will fail on non-Windows systems or Windows versions without this support

make_app_dpi_aware()  # Call the function to make app DPI aware

def get_printers():
    printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
    return printers

def generate_receipt_text():
    # Header
    receipt_text = "\t\tHS CARGO\n"
    receipt_text += "\t Thailand - Myanmar CARGO\n"
    receipt_text += "\tထိုင်း - မြန်မာ ကုန်စည် အမြန်ပို့ဆောင်ရေး\n"
    receipt_text += "Invoice No: INV240100001\n"
    receipt_text += "Customer Name: Sender Name\n"
    receipt_text += "Phone: Sender Phone\n"
    receipt_text += "\n"  # Spacer
    
    # Item list (Simplified for demonstration. Expand based on actual requirements.)
    items = [
        {"id": "HST2401000001", "name": "Ye Htut Khaung", "phone": "Receiver Phone", "price": "165000"},
        {"id": "HST2401000002", "name": "Pyae Phyo Minn", "phone": "Receiver Phone", "price": "300000"},
        {"id": "HST2401000003", "name": "Yee Yee Lwin", "phone": "Receiver Phone", "price": "20000"},
        {"id": "HST2401000004", "name": "U Zaw Naing", "phone": "Receiver Phone", "price": "142000"},
        {"id": "HST2401000005", "name": "Ei Ei Khin", "phone": "Receiver Phone", "price": "300000"},
        {"id": "HST2401000006", "name": "Thant Sin Aung", "phone": "Receiver Phone", "price": "400000"},
    ]
    
    for item in items:
        receipt_text += f'{item["id"]}\t{item["name"]}\t{item["price"]}\n\t\t{item["phone"]}\n'
    
    # Footer
    receipt_text += "\nNet Total:    1461000\n"
    receipt_text += "Total Item:   8\n"
    receipt_text += "\nPrinted by: Staff Name\n"
    receipt_text += "\n\tAll right reserved by;\n"
    receipt_text += "\twww.hs-cargo.com\n"
    # Include additional footer text as required
    
    return receipt_text

def print_test_receipt(printer_name, receipt_text):
    # Assuming you have already chosen a printer through the GUI
    filename = tempfile.mktemp(suffix=".txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(generate_receipt_text())  # Use the generated receipt text
    # Printing the file
    win32api.ShellExecute(0, "print", filename, f'/d:"{printer_name}"', ".", 0)


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            printer_name = data.get('printer_name')  # Get printer name from POST data

            if 'action' in data and data['action'] == 'print':
                receipt_text = generate_receipt_text()
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
app.title("Bifrost Bridge")
app.geometry("400x200")

printer_label = ttk.Label(app, text="Select Printer:")
printer_label.pack(pady=5)

printer_combo = ttk.Combobox(app, values=get_printers())
printer_combo.pack(pady=5)

# Start the server in a separate thread to keep the GUI responsive
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

app.mainloop()
