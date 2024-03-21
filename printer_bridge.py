import ctypes
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import tkinter as tk
from tkinter import ttk
import win32print
import win32api
import tempfile
import logging

# Setup logging
logging.basicConfig(filename='printer_bridge.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Make the application DPI aware to improve appearance on high DPI displays
def make_app_dpi_aware():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 1: System DPI aware, 2: Per monitor DPI aware
        logging.info("Application made DPI aware successfully")
    except (AttributeError, Exception) as e:
        logging.exception("Failed to make the application DPI aware")
        pass  # This will fail on non-Windows systems or Windows versions without this support

make_app_dpi_aware()  # Call the function to make app DPI aware

def get_printers():
    try:
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
        logging.info(f"Printers found: {printers}")
        return printers
    except Exception as e:
        logging.exception("Failed to get printers")
        return []

def generate_receipt_text():
    # Header
    receipt_text = "\t\tHS CARGO\n"
    receipt_text += "\t Thailand - Myanmar CARGO\n"
    receipt_text += "\tထိုင်း - မြန်မာ ကုန်စည် အမြန်ပို့ဆောင်ရေး\n"
    receipt_text += "Invoice No: INV240100001\n"
    receipt_text += "Customer Name: Sender Name\n"
    receipt_text += "Phone: Sender Phone\n"
    receipt_text += "\n"  # Spacer
    
    # Item list
    items = [
        # Your items here
    ]
    
    for item in items:
        receipt_text += f'{item["id"]}\t{item["name"]}\t{item["price"]}\n\t\t{item["phone"]}\n'
    
    # Footer
    receipt_text += "\nNet Total:    XXXXX\n"
    receipt_text += "Total Item:   XXX\n"
    receipt_text += "\nPrinted by: Staff Name\n"
    receipt_text += "\n\tAll right reserved by;\n"
    receipt_text += "\twww.hs-cargo.com\n"
    
    return receipt_text

def print_test_receipt(printer_name, receipt_text):
    try:
        # Assuming you have already chosen a printer through the GUI
        filename = tempfile.mktemp(suffix=".txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(generate_receipt_text())  # Use the generated receipt text
        # Printing the file
        win32api.ShellExecute(0, "print", filename, f'/d:"{printer_name}"', ".", 0)
        logging.info(f"Receipt printed successfully on {printer_name}")
    except Exception as e:
        logging.exception(f"Failed to print receipt on {printer_name}")

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
                logging.error("Received invalid action value in request")
        except json.JSONDecodeError:
            self.send_error(400, "Bad Request: Could not decode JSON")
            logging.exception("JSON Decode Error in POST request")

def run_server(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    try:
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        logging.info(f'Starting HTTP server on port {port}...')
        httpd.serve_forever()
    except Exception as e:
        logging.exception(f"Failed to start HTTP server on port {port}")

# GUI Setup
def setup_gui():
    app = tk.Tk()
    app.title("Printer Bridge")
    app.geometry("400x200")

    try:
        printer_label = ttk.Label(app, text="Select Printer:")
        printer_label.pack(pady=5)

        printer_combo = ttk.Combobox(app, values=get_printers())
        printer_combo.pack(pady=5)
        logging.info("GUI setup completed successfully.")
    except Exception as e:
        logging.exception("Failed to setup GUI")

    return app

def main():
    make_app_dpi_aware()  # Make application DPI aware
    app = setup_gui()  # Setup GUI

    # Start the server in a separate thread to keep the GUI responsive
    server_thread = threading.Thread(target=run_server, args=(HTTPServer, RequestHandler, 8080))
    server_thread.daemon = True
    server_thread.start()
    
    app.mainloop()

if __name__ == "__main__":
    main()

