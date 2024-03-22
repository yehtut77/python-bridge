import tkinter as tk
from tkinter import ttk, messagebox
import usb.core
import usb.util
import win32print
import json
import os

class PrinterApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.load_selected_printer_info()
        self.printers = self.list_win_printers()
        self.usb_devices = self.list_usb_devices()
        self.populate_printer_combobox()

    def setup_ui(self):
        self.root.title("Printer Selection App")
        self.root.geometry("400x200")

        # Printer selection combobox
        self.printer_label = ttk.Label(self.root, text="Select Printer:")
        self.printer_label.pack(pady=5)

        self.printer_combo = ttk.Combobox(self.root)
        self.printer_combo.pack(pady=5)

        self.select_button = ttk.Button(self.root, text="Select Printer", command=self.select_printer)
        self.select_button.pack(pady=5)

    def populate_printer_combobox(self):
        self.printer_combo['values'] = self.list_win_printers()
        if self.printer_combo['values']:
            self.printer_combo.current(0)

    def list_win_printers(self):
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        return [printer[2] for printer in printers]

    def list_usb_devices(self):
        devices = usb.core.find(find_all=True)
        usb_devices = []
        for device in devices:
            try:
                usb_devices.append({
                    "vid": device.idVendor,
                    "pid": device.idProduct,
                    "manufacturer": usb.util.get_string(device, device.iManufacturer),
                    "product": usb.util.get_string(device, device.iProduct)
                })
            except Exception as e:
                continue  # Skip devices that we can't access
        return usb_devices

    def select_printer(self):
        selected_printer_name = self.printer_combo.get()
        messagebox.showinfo("Selected Printer", f"Printer: {selected_printer_name}")
        # Here, you'd match and save the printer's VID and PID for `python-escpos`
        # For demonstration, just log the selected printer name
        print(f"Selected Printer: {selected_printer_name}")

    def load_selected_printer_info(self):
        # Implement loading of printer info (VID, PID) if already selected
        pass

    def save_selected_printer_info(self, printer_info):
        # Implement saving of selected printer info (VID, PID)
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = PrinterApp(root)
    root.mainloop()
