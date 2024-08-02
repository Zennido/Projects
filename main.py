import qrcode
from PIL import Image
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

def generate_qr_code(data, file_path, file_type):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    if file_type == "PNG":
        img.save(file_path + ".png")
    elif file_type == "GIF":
        img.save(file_path + ".gif")

def on_generate_qr_code():
    data = data_entry.get()
    file_name = file_name_entry.get()
    file_type = file_type_combobox.get()
    file_path = file_path_var.get()

    if data and file_name and file_type and file_path:
        full_path = f"{file_path}/{file_name}"
        generate_qr_code(data, full_path, file_type)
        result_label.configure(text=f"QR code saved as {file_name}.{file_type.lower()}")
    else:
        result_label.configure(text="Please provide all fields.")


def select_path():
    path = filedialog.askdirectory()
    file_path_var.set(path)

app = ctk.CTk() 
app.title("QR Code Generator")
app.geometry("500x500") 


frame = ctk.CTkFrame(app)
frame.pack(padx=20, pady=20, fill='both', expand=True)
title_label = ctk.CTkLabel(frame, text="QR Code Generator")
title_label.pack()

data_label = ctk.CTkLabel(frame, text="Data to encode:")
data_label.pack(pady=5)
data_entry = ctk.CTkEntry(frame)
data_entry.pack(pady=5, fill='x')

file_name_label = ctk.CTkLabel(frame, text="File name:")
file_name_label.pack(pady=5)
file_name_entry = ctk.CTkEntry(frame)
file_name_entry.pack(pady=5, fill='x')

file_type_label = ctk.CTkLabel(frame, text="Select file type:")
file_type_label.pack(pady=5)
file_type_combobox = ctk.CTkComboBox(frame, values=["PNG", "GIF"])
file_type_combobox.pack(pady=5)

file_path_var = tk.StringVar()
file_path_label = ctk.CTkLabel(frame, text="Select save path:")
file_path_label.pack(pady=5)
file_path_entry = ctk.CTkEntry(frame, textvariable=file_path_var)
file_path_entry.pack(pady=5, fill='x')
select_path_button = ctk.CTkButton(frame, text="Browse", command=select_path)
select_path_button.pack(pady=5)

generate_button = ctk.CTkButton(frame, text="Generate QR Code", command=on_generate_qr_code)
generate_button.pack(pady=10)

result_label = ctk.CTkLabel(frame, text="")
result_label.pack(pady=5)

app.mainloop()
