import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import os
from image_processing import (
    to_grayscale, to_binary, arithmetic_add, logic_and,
    apply_filter, show_histogram, morphology
)

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Pengolahan Citra Digital")
        self.root.geometry("1080x720")
        self.root.configure(bg="#e9f1f7")
        self.image = None
        self.original_image = None  
        self.displayed_image = None
        self.last_operation = None

        # Header
        header_frame = tk.Frame(root, bg="#2b6777", pady=10)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Selamat Datang di Aplikasi PixeLNS",
                 font=("Helvetica", 20, "bold"), fg="white", bg="#2b6777").pack()
        tk.Label(header_frame, text="Silakan pilih fitur di bawah untuk memulai",
                 font=("Helvetica", 12), fg="white", bg="#2b6777").pack()

        # Frame tombol
        self.btn_frame = tk.Frame(root, bg="#e9f1f7")
        self.btn_frame.pack(pady=20)

        self.button_styles = {
            "default": {"bg": "#41b4bd", "fg": "white"},
            "grayscale": {"bg": "#696464", "fg": "white"},
            "binary": {"bg": "#FF8C00", "fg": "white"},
            "dual": {"bg": "#8A2BE2", "fg": "white"},
            "edge": {"bg": "#DC143C", "fg": "white"},
            "histogram": {"bg": "#4682B4", "fg": "white"},
            "morph": {"bg": "#8A2BE2", "fg": "white"},
        }

        self.create_button("Input Gambar", self.load_image, 0, 0, "default")
        self.create_button("Grayscale", self.process_grayscale, 0, 1, "grayscale")
        self.create_button("Biner", self.process_binary, 2, 2, "binary") 
        self.create_button("Tambah Kecerahan (2 Gambar)", self.process_add_dual_image, 1, 0, "dual") 
        self.create_button("Logika AND (2 Gambar)", self.process_and_dual_image, 1, 1, "dual")
        self.create_button("Histogram", self.show_hist, 2, 0, "histogram")
        self.create_button("Edge Detection", lambda: self.process_filter('edge'), 2, 1, "edge")
        self.create_button("Dilasi (2 SE)", self.process_morph, 1, 2, "morph") 
        self.create_button("Reset Gambar", self.reset_to_original, 0, 2, "default")  # Tombol reset

        # Frame gambar
        self.image_frame = tk.Frame(root, bg="#e9f1f7")
        self.image_frame.pack(pady=10)

        self.create_image_display_area()
        self.reset_frame_layout(1)

    def create_button(self, text, command, row, col, style_key):
        style = self.button_styles.get(style_key, {})
        btn = tk.Button(self.btn_frame, text=text, command=command,
                        bg=style.get("bg"), fg=style.get("fg"),
                        font=("Helvetica", 10, "bold"),
                        width=30, height=2, relief="flat", bd=0)
        btn.grid(row=row, column=col, padx=10, pady=10)
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#444"))
        btn.bind("<Leave>", lambda e, b=btn, bg=style.get("bg"): b.config(bg=bg))

    def create_image_display_area(self):
        def create_image_box():
            frame = tk.Frame(self.image_frame, bd=2, relief="groove", bg="white", padx=5, pady=5)
            img_label = tk.Label(frame, bg="white")
            img_label.pack()
            label_desc = tk.Label(frame, text="", font=("Arial", 10), bg="white")
            label_desc.pack(pady=(5, 0))
            return frame, img_label, label_desc

        self.frame1, self.image_label1, self.label1_desc = create_image_box()
        self.frame2, self.image_label2, self.label2_desc = create_image_box()
        self.frame3, self.image_label3, self.label3_desc = create_image_box()

    def show_frame(self, frame, column):
        frame.grid(row=0, column=column, padx=10)

    def hide_frame(self, frame):
        frame.grid_forget()

    def reset_frame_layout(self, visible_frames=1):
        self.hide_frame(self.frame1)
        self.hide_frame(self.frame2)
        self.hide_frame(self.frame3)
        if visible_frames == 1:
            self.show_frame(self.frame1, 1)
        elif visible_frames == 3:
            self.show_frame(self.frame1, 0)
            self.show_frame(self.frame2, 1)
            self.show_frame(self.frame3, 2)

    def show_image(self, img, label_widget):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img_rgb).resize((300, 300))
        tk_image = ImageTk.PhotoImage(im_pil)
        label_widget.config(image=tk_image)
        label_widget.image = tk_image
        if label_widget == self.image_label1:
            self.displayed_image = img

    def clear_labels(self):
        for lbl in [self.image_label1, self.image_label2, self.image_label3]:
            lbl.config(image='')
            lbl.image = None
        self.label1_desc.config(text="")
        self.label2_desc.config(text="")
        self.label3_desc.config(text="")

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = cv2.imread(file_path)
            self.original_image = self.image.copy()
            self.clear_labels()
            self.reset_frame_layout(1)
            self.show_image(self.image, self.image_label1)
            self.label1_desc.config(text="Input")
            self.last_operation = "input"

    def reset_to_original(self):
        if self.original_image is not None:
            self.clear_labels()
            self.reset_frame_layout(1)
            self.show_image(self.original_image, self.image_label1)
            self.label1_desc.config(text="Kembali ke Gambar Asli")
            self.image = self.original_image.copy()
            self.displayed_image = self.original_image.copy()
            self.last_operation = "input"
        else:
            messagebox.showinfo("Info", "Belum ada gambar yang dimuat.")

    def process_grayscale(self):
        if self.image is not None:
            gray = to_grayscale(self.image)
            result_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            self.clear_labels()
            self.reset_frame_layout(1)
            self.show_image(result_bgr, self.image_label1)
            self.label1_desc.config(text="Grayscale")
            self.displayed_image = result_bgr
            self.last_operation = "grayscale"
            os.makedirs("foto/output", exist_ok=True)
            cv2.imwrite("foto/output/hasil_grayscale.png", gray)
        else:
            messagebox.showinfo("Info", "Silakan input gambar terlebih dahulu.")

    def process_binary(self):
        if self.image is not None:
            binary = to_binary(self.image)
            result_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
            self.clear_labels()
            self.reset_frame_layout(1)
            self.show_image(result_bgr, self.image_label1)
            self.label1_desc.config(text="Biner")
            self.displayed_image = result_bgr
            self.last_operation = "binary"
            os.makedirs("foto/output", exist_ok=True)
            cv2.imwrite("foto/output/hasil_biner.png", binary)
        else:
            messagebox.showinfo("Info", "Silakan input gambar terlebih dahulu.")

    def process_filter(self, mode):
        if self.image is not None:
            result = apply_filter(self.image, mode)
            self.clear_labels()
            self.reset_frame_layout(1)
            self.show_image(result, self.image_label1)
            self.label1_desc.config(text="Edge Detection")
            self.displayed_image = result
            self.last_operation = "edge"
            os.makedirs("foto/output", exist_ok=True)
            cv2.imwrite("foto/output/hasil_edge.png", result)
        else:
            messagebox.showinfo("Info", "Silakan input gambar terlebih dahulu.")

    def show_hist(self):
        if self.last_operation in ["grayscale", "binary", "edge", "add"] and self.displayed_image is not None:
            show_histogram(self.displayed_image)
        elif self.last_operation == "input" and self.image is not None:
            show_histogram(self.image)
        elif self.last_operation in ["and", "dilate"]:
            messagebox.showinfo("Info", "Histogram tidak tersedia untuk hasil operasi ini.")
        else:
            messagebox.showinfo("Info", "Silakan input gambar terlebih dahulu.")

    def process_add_dual_image(self):
        file1 = filedialog.askopenfilename(title="Pilih Gambar Pertama")
        file2 = filedialog.askopenfilename(title="Pilih Gambar Kedua")
        if file1 and file2:
            img1 = cv2.imread(file1)
            img2 = cv2.imread(file2)
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            added = cv2.add(img1, img2)
            self.clear_labels()
            self.reset_frame_layout(3)
            self.show_image(img1, self.image_label1)
            self.show_image(img2, self.image_label2)
            self.show_image(added, self.image_label3)
            self.label1_desc.config(text="Gambar 1")
            self.label2_desc.config(text="Gambar 2")
            self.label3_desc.config(text="Hasil Penjumlahan")
            self.displayed_image = added
            self.image = None
            self.last_operation = "add"
            os.makedirs("foto/output", exist_ok=True)
            cv2.imwrite("foto/output/hasil_penjumlahan.png", added)

    def process_and_dual_image(self):
        file1 = filedialog.askopenfilename(title="Pilih Gambar Pertama")
        file2 = filedialog.askopenfilename(title="Pilih Gambar Kedua")
        if file1 and file2:
            img1 = cv2.imread(file1)
            img2 = cv2.imread(file2)
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            and_result = logic_and(img1, img2)
            self.clear_labels()
            self.reset_frame_layout(3)
            self.show_image(img1, self.image_label1)
            self.show_image(img2, self.image_label2)
            self.show_image(and_result, self.image_label3)
            self.label1_desc.config(text="Gambar 1")
            self.label2_desc.config(text="Gambar 2")
            self.label3_desc.config(text="Logika AND")
            self.displayed_image = None
            self.image = None
            self.last_operation = "and"
            os.makedirs("foto/output", exist_ok=True)
            cv2.imwrite("foto/output/hasil_and.png", and_result)

    def process_morph(self):
        file_path = filedialog.askopenfilename(title="Pilih Gambar untuk Dilasi")
        if file_path:
            img = cv2.imread(file_path)
            result1, result2 = morphology(img)
            result1_bgr = cv2.cvtColor(result1, cv2.COLOR_GRAY2BGR)
            result2_bgr = cv2.cvtColor(result2, cv2.COLOR_GRAY2BGR)
            self.clear_labels()
            self.reset_frame_layout(3)
            self.show_image(img, self.image_label1)
            self.show_image(result1_bgr, self.image_label2)
            self.show_image(result2_bgr, self.image_label3)
            self.label1_desc.config(text="Gambar Input")
            self.label2_desc.config(text="Dilasi: SE Full Square")
            self.label3_desc.config(text="Dilasi: SE Silang")
            self.displayed_image = None
            self.image = None
            self.last_operation = "dilate"
            os.makedirs("foto/output", exist_ok=True)
            cv2.imwrite("foto/output/hasil_dilasi1.png", result1)
            cv2.imwrite("foto/output/hasil_dilasi2.png", result2)

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
