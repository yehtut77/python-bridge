import tkinter as tk
from tkinter import ttk
import win32print
import win32api
import tempfile

def get_printers():
    printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
    return printers

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

def on_print_button():
    selected_printer = printer_combo.get()
    print_test_receipt(selected_printer)
    print(f"Sent a test receipt to {selected_printer}")

app = tk.Tk()
app.title("Printer Bridge with win32print")
app.geometry("400x200")

# Dropdown menu for printer selection
printer_label = ttk.Label(app, text="Select Printer:")
printer_label.pack(pady=5)
printer_combo = ttk.Combobox(app, values=get_printers())
printer_combo.pack(pady=5)

# Print button
print_button = ttk.Button(app, text="Print Test Receipt", command=on_print_button)
print_button.pack(pady=20)

app.mainloop()
