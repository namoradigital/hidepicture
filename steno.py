import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os

class SteganoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganografi - Sembunyikan Pesan dalam Gambar")
        self.root.geometry("800x600")
        
        # Variabel
        self.image_path = ""
        self.original_image = None
        self.modified_image = None
        
        # Frame untuk gambar
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=10)
        
        # Label untuk gambar asli
        self.original_label = tk.Label(self.image_frame, text="Gambar Asli")
        self.original_label.grid(row=0, column=0, padx=10)
        
        # Canvas untuk gambar asli
        self.original_canvas = tk.Canvas(self.image_frame, width=300, height=300)
        self.original_canvas.grid(row=1, column=0, padx=10)
        
        # Label untuk gambar modifikasi
        self.modified_label = tk.Label(self.image_frame, text="Gambar dengan Pesan Tersembunyi")
        self.modified_label.grid(row=0, column=1, padx=10)
        
        # Canvas untuk gambar modifikasi
        self.modified_canvas = tk.Canvas(self.image_frame, width=300, height=300)
        self.modified_canvas.grid(row=1, column=1, padx=10)
        
        # Frame untuk kontrol
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)
        
        # Tombol untuk memilih gambar
        self.select_button = tk.Button(self.control_frame, text="Pilih Gambar", command=self.select_image)
        self.select_button.grid(row=0, column=0, padx=5)
        
        # Text area untuk pesan
        self.message_label = tk.Label(self.control_frame, text="Pesan Rahasia:")
        self.message_label.grid(row=1, column=0, sticky="w", pady=(10, 0))
        
        self.message_text = tk.Text(self.control_frame, width=50, height=5)
        self.message_text.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Tombol untuk menyembunyikan pesan
        self.encode_button = tk.Button(self.control_frame, text="Sembunyikan Pesan", command=self.encode_message)
        self.encode_button.grid(row=3, column=0, padx=5, pady=5)
        
        # Tombol untuk mengekstrak pesan
        self.decode_button = tk.Button(self.control_frame, text="Ekstrak Pesan", command=self.decode_message)
        self.decode_button.grid(row=3, column=1, padx=5, pady=5)
        
        # Tombol untuk menyimpan gambar
        self.save_button = tk.Button(self.control_frame, text="Simpan Gambar", command=self.save_image, state=tk.DISABLED)
        self.save_button.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Label status
        self.status_label = tk.Label(self.root, text="Pilih gambar untuk memulai", fg="blue")
        self.status_label.pack(pady=10)
    
    def select_image(self):
        """Memilih gambar dari file dialog"""
        file_path = filedialog.askopenfilename(
            title="Pilih Gambar",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.image_path = file_path
            try:
                self.original_image = Image.open(file_path)
                self.display_image(self.original_image, self.original_canvas)
                
                # Reset modified image
                self.modified_image = None
                self.modified_canvas.delete("all")
                self.save_button.config(state=tk.DISABLED)
                
                self.status_label.config(text=f"Gambar dipilih: {os.path.basename(file_path)}", fg="green")
            except Exception as e:
                messagebox.showerror("Error", f"Tidak dapat membuka gambar: {e}")
    
    def display_image(self, image, canvas):
        """Menampilkan gambar pada canvas"""
        # Resize image to fit canvas
        width, height = image.size
        ratio = min(300/width, 300/height)
        new_size = (int(width * ratio), int(height * ratio))
        resized_image = image.resize(new_size, Image.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(resized_image)
        
        # Update canvas
        canvas.delete("all")
        canvas.image = photo  # Keep reference
        canvas.create_image(150, 150, image=photo, anchor=tk.CENTER)
    
    def encode_message(self):
        """Menyembunyikan pesan dalam gambar"""
        if not self.original_image:
            messagebox.showwarning("Peringatan", "Silakan pilih gambar terlebih dahulu")
            return
        
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Peringatan", "Silakan masukkan pesan terlebih dahulu")
            return
        
        try:
            # Convert image to RGB if not already
            if self.original_image.mode != 'RGB':
                img = self.original_image.convert('RGB')
            else:
                img = self.original_image.copy()
            
            # Convert message to binary
            binary_message = ''.join(format(ord(c), '08b') for c in message)
            binary_message += '1111111111111110'  # Adding delimiter
            
            # Calculate maximum message length
            max_length = img.size[0] * img.size[1] * 3
            if len(binary_message) > max_length:
                messagebox.showerror("Error", f"Pesan terlalu panjang untuk gambar ini. Maksimum: {max_length//8} karakter")
                return
            
            # Convert image to numpy array with proper type
            img_array = np.array(img, dtype=np.uint8)
            flat = img_array.flatten()
            
            # Embed message in LSB with boundary checking
            for i in range(len(binary_message)):
                pixel = flat[i]
                bit = int(binary_message[i])
                # Clear LSB and set to new bit value
                new_pixel = (pixel & 0xFE) | bit
                # Ensure value stays within uint8 bounds
                flat[i] = np.uint8(new_pixel)
            
            # Reshape back to original
            img_array = flat.reshape(img_array.shape)
            self.modified_image = Image.fromarray(img_array)
            
            # Display modified image
            self.display_image(self.modified_image, self.modified_canvas)
            self.save_button.config(state=tk.NORMAL)
            
            self.status_label.config(text="Pesan berhasil disembunyikan dalam gambar!", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyembunyikan pesan: {str(e)}")
    
    def decode_message(self):
        """Mengekstrak pesan dari gambar"""
        if not self.original_image:
            messagebox.showwarning("Peringatan", "Silakan pilih gambar terlebih dahulu")
            return
        
        try:
            # Convert image to RGB if not already
            if self.original_image.mode != 'RGB':
                img = self.original_image.convert('RGB')
            else:
                img = self.original_image
            
            # Convert image to numpy array with proper type
            img_array = np.array(img, dtype=np.uint8)
            flat = img_array.flatten()
            
            # Extract LSBs
            binary_message = ''.join([str(px & 1) for px in flat])
            
            # Find delimiter
            delimiter = '1111111111111110'
            if delimiter in binary_message:
                binary_message = binary_message[:binary_message.index(delimiter)]
            else:
                messagebox.showinfo("Info", "Tidak ditemukan pesan dalam gambar")
                return
            
            # Convert binary to string
            message = ''
            for i in range(0, len(binary_message), 8):
                byte = binary_message[i:i+8]
                message += chr(int(byte, 2))
            
            self.message_text.delete("1.0", tk.END)
            self.message_text.insert("1.0", message)
            
            self.status_label.config(text="Pesan berhasil diekstrak dari gambar!", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekstrak pesan: {str(e)}")
    
    def save_image(self):
        """Menyimpan gambar dengan pesan tersembunyi"""
        if not self.modified_image:
            messagebox.showwarning("Peringatan", "Tidak ada gambar yang dimodifikasi untuk disimpan")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Simpan Gambar",
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                self.modified_image.save(file_path)
                self.status_label.config(text=f"Gambar berhasil disimpan sebagai {os.path.basename(file_path)}", fg="green")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan gambar: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganoApp(root)
    root.mainloop()