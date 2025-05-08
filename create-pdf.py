import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageTk
import os

class PDFGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Generator")
        self.root.geometry("600x600")

        self.images = []

        self.label = tk.Label(root, text="Select images to add to PDF", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.add_button = tk.Button(root, text="Add Images", command=self.add_images)
        self.add_button.pack(pady=10)

        self.filename_label = tk.Label(root, text="Selected File:", font=("Helvetica", 12))
        self.filename_label.pack(pady=5)

        self.preview_label = tk.Label(root, text="Image Preview", font=("Helvetica", 12))
        self.preview_label.pack(pady=10)

        self.preview_canvas = tk.Canvas(root, width=300, height=300, bg="white")
        self.preview_canvas.pack(pady=10)

        self.button = tk.Button(root, text="Generate PDF", command=self.generate_pdf)
        self.button.pack(pady=20)

    def add_images(self):
        files = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                self.images.append(file)
                self.label.config(text=f"Images added: {len(self.images)}")
                self.update_preview(file)
                self.filename_label.config(text=f"Selected File: {os.path.basename(file)}")

    def update_preview(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(img)
        self.preview_canvas.create_image(150, 150, image=photo)
        self.preview_canvas.image = photo

    def generate_pdf(self):
        if not self.images:
            messagebox.showerror("Error", "No images added!")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not filename:
            return

        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        for image_path in self.images:
            img = Image.open(image_path)
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height

            # 如果是横图，则使用 landscape 页面方向
            if aspect_ratio > 1:
                page_size = (height, width)  # 横向页面
                pdf_img = img.rotate(90, expand=True)
                img_width, img_height = img.size
                img_width, img_height = img_height, img_width
            else:
                page_size = letter  # 纵向页面
                pdf_img = img

            c.setPageSize(page_size)
            pdf_width, pdf_height = page_size

            scale = min(pdf_width / img_width, pdf_height / img_height)
            new_width = img_width * scale
            new_height = img_height * scale

            x = (pdf_width - new_width) / 2
            y = (pdf_height - new_height) / 2

            c.drawImage(ImageReader(pdf_img), x, y, new_width, new_height)
            c.showPage()

        c.save()
        messagebox.showinfo("Success", f"PDF created successfully at {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFGenerator(root)
    root.mainloop()