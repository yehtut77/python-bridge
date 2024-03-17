import tkinter as tk
from tkinter import ttk
import cups

def get_printers():
    conn = cups.Connection()
    printers = conn.getPrinters()
    return list(printers.keys())

def print_test_receipt(printer_name):
    conn = cups.Connection()
    # Preparing a simple text file to print
    filename = "/tmp/test_receipt.txt"
    with open(filename, "w") as f:
        f.write("***** POS RECEIPT *****\n\n")
        f.write("Item A: $5.00\n")
        f.write("Item B: $3.50\n")
        f.write("\nThank You!\n")
    # Printing the file
    conn.printFile(printer_name, filename, "Test POS Receipt", {})

def on_print_button():
    selected_printer = printer_combo.get()
    print_test_receipt(selected_printer)
    print(f"Sent a test receipt to {selected_printer}")

app = tk.Tk()
app.title("Printer Bridge with PyCUPS")
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
