import os
import sqlite3
import tkinter as tk
from PIL import Image, ImageTk, ExifTags
from tkinter import messagebox, filedialog
from dateutil.parser import parse

# Connect to SQLite database
conn = sqlite3.connect('image_info.db')
c = conn.cursor()

# Create a table
c.execute("""
CREATE TABLE IF NOT EXISTS Images(
    FileName TEXT,
    FolderName TEXT,
    CreationDate TEXT,
    SelectedOption TEXT)
""")

# Commit changes and close connection
conn.commit()
conn.close()

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.folder_path = ""
        self.image_list = []
        self.image_index = 0
        self.list_options = ["Option 1", "Option 2", "Option 3"]
        self.selected_option = tk.StringVar()

        self.canvas = tk.Canvas(self.root, width=500, height=500)
        self.canvas.pack()

        self.option_menu = tk.OptionMenu(self.root, self.selected_option, *self.list_options)
        self.option_menu.pack()

        self.save_button = tk.Button(self.root, text="Save", command=self.save_data)
        self.save_button.pack()

        self.next_button = tk.Button(self.root, text="Next", command=self.next_image)
        self.next_button.pack()

        self.open_folder_button = tk.Button(self.root, text="Open Folder", command=self.open_folder)
        self.open_folder_button.pack()

    def open_folder(self):
        self.folder_path = filedialog.askdirectory()
        self.image_list = [f for f in os.listdir(self.folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if self.image_list:
            self.image_index = 0
            self.load_image()

    def load_image(self):
        img_path = os.path.join(self.folder_path, self.image_list[self.image_index])
        img = Image.open(img_path)
        img.thumbnail((500,500), Image.ANTIALIAS)
        photo_img = ImageTk.PhotoImage(img)

        self.canvas.create_image(0, 0, image=photo_img, anchor='nw')
        self.canvas.image = photo_img

    def next_image(self):
        if self.image_index < len(self.image_list) - 1:
            self.image_index += 1
            self.load_image()
        else:
            messagebox.showinfo("Info", "This is the last image in the folder.")

    def save_data(self):
        img_path = os.path.join(self.folder_path, self.image_list[self.image_index])
        img = Image.open(img_path)

        exif_data = img._getexif()
        for tag, value in exif_data.items():
            if ExifTags.TAGS.get(tag) == 'DateTime':
                creation_date = parse(value)

        conn = sqlite3.connect('image_info.db')
        c = conn.cursor()

        # Insert values into the table
        c.execute("""
        INSERT INTO Images (FileName, FolderName, CreationDate, SelectedOption) 
        VALUES (?, ?, ?, ?)""",
                  (self.image_list[self.image_index], self.folder_path, creation_date, self.selected_option.get()))

        # Commit changes and close connection
        conn.commit()
        conn.close()

        self.next_image()

root = tk.Tk()
app = ImageApp(root)
root.mainloop()

