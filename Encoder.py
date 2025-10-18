import os
import base64
import threading
import numpy as np
from PIL import Image
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import filedialog, messagebox

# === Password Key ===
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_message(message, password):
    salt = os.urandom(16)
    key = derive_key(password, salt)
    cipher = Fernet(key)
    encrypted = cipher.encrypt(message.encode())
    return base64.b64encode(salt + encrypted).decode()

def decrypt_message(encrypted_message, password):
    data = base64.b64decode(encrypted_message)
    salt, encrypted = data[:16], data[16:]
    key = derive_key(password, salt)
    cipher = Fernet(key)
    return cipher.decrypt(encrypted).decode()

# === Vectorized LSB with progress callback ===
def embed_message_in_image(image_path, message, output_path, progress_callback=None):
    img = Image.open(image_path).convert("RGB")
    pixels = np.array(img, dtype=np.uint8)
    message += "EOF"
    binary_message = np.array([int(b) for c in message for b in format(ord(c),'08b')], dtype=np.uint8)
    total_bits = binary_message.size
    flat_pixels = pixels.flatten()
    if total_bits > flat_pixels.size:
        raise ValueError("Message too long for the image!")

    chunk_size = max(total_bits // 200, 1)
    for i in range(0, total_bits, chunk_size):
        end = min(i + chunk_size, total_bits)
        flat_pixels[i:end] = (flat_pixels[i:end] & ~1) | binary_message[i:end]
        if progress_callback:
            progress_callback(end / total_bits * 100)

    Image.fromarray(flat_pixels.reshape(pixels.shape)).save(output_path)
    if progress_callback:
        progress_callback(100)

def extract_message_from_image(image_path, progress_callback=None):
    img = Image.open(image_path).convert("RGB")
    pixels = np.array(img, dtype=np.uint8)
    flat_pixels = pixels.flatten()
    total_bits = flat_pixels.size
    bits = np.zeros(total_bits, dtype=np.uint8)
    chunk_size = max(total_bits // 200, 1)
    for i in range(0, total_bits, chunk_size):
        end = min(i + chunk_size, total_bits)
        bits[i:end] = flat_pixels[i:end] & 1
        if progress_callback:
            progress_callback(end / total_bits * 100)
    chars = np.packbits(bits)
    decoded = ''.join(chr(b) for b in chars)
    if "EOF" in decoded:
        decoded = decoded.split("EOF")[0]
    if progress_callback:
        progress_callback(100)
    return decoded

# === CLI-style GUI ===
class CLIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔒 Steganography CLI Tool")
        self.root.geometry("880x760")
        self.root.configure(bg="#1e1e1e")  # dark theme
        self.root.resizable(False, False)

        self.input_image_encode = ""
        self.input_image_decode = ""

        # Fonts/colors
        self.font = ("Consolas", 11)
        self.fg_color = "#d4d4d4"
        self.input_bg = "#2d2d2d"

        # Header
        self.header = tk.Label(root, text="🖼️ Secure Image Steganography CLI", font=("Consolas", 18, "bold"),
                               bg="#1e1e1e", fg="#4ec9b0")
        self.header.pack(pady=15)

        container = tk.Frame(root, bg="#1e1e1e")
        container.pack(padx=20, pady=5, fill="both", expand=True)

        # --- ENCODE ---
        encode_frame = tk.LabelFrame(container, text="Encode Message", fg="#d4d4d4", bg="#1e1e1e",
                                     font=self.font, padx=10, pady=10)
        encode_frame.pack(fill="x", pady=5)
        tk.Label(encode_frame, text="Message to Hide:", fg=self.fg_color, bg="#1e1e1e", font=self.font).grid(row=0, column=0, sticky="w")
        self.message_entry = tk.Text(encode_frame, height=4, width=80, bg=self.input_bg, fg=self.fg_color,
                                     insertbackground="white", font=self.font)
        self.message_entry.grid(row=1, column=0, columnspan=3, pady=5)
        tk.Label(encode_frame, text="Password:", fg=self.fg_color, bg="#1e1e1e", font=self.font).grid(row=2, column=0, sticky="w")
        self.password_entry = tk.Entry(encode_frame, width=35, show="*", bg=self.input_bg, fg=self.fg_color, insertbackground="white")
        self.password_entry.grid(row=2, column=1, sticky="w")
        tk.Button(encode_frame, text="Choose Image", command=self.select_encode_image, bg="#007acc", fg="white",
                  font=self.font).grid(row=3, column=1, sticky="w", pady=3)
        self.encode_image_label = tk.Label(encode_frame, text="No image selected", fg="gray", bg="#1e1e1e", font=self.font)
        self.encode_image_label.grid(row=3, column=2, sticky="w")
        tk.Label(encode_frame, text="Output File Name:", fg=self.fg_color, bg="#1e1e1e", font=self.font).grid(row=4, column=0, sticky="w")
        self.output_entry = tk.Entry(encode_frame, width=35, bg=self.input_bg, fg=self.fg_color, insertbackground="white")
        self.output_entry.grid(row=4, column=1, sticky="w")
        tk.Button(encode_frame, text="🔐 Encode & Save", command=self.thread_encode, bg="#4ec9b0", fg="black", font=self.font).grid(row=5, column=0, columnspan=2, pady=5)

        # --- DECODE ---
        decode_frame = tk.LabelFrame(container, text="Decode Message", fg="#d4d4d4", bg="#1e1e1e",
                                     font=self.font, padx=10, pady=10)
        decode_frame.pack(fill="x", pady=5)
        tk.Button(decode_frame, text="Choose Image", command=self.select_decode_image, bg="#007acc", fg="white", font=self.font).grid(row=0, column=1, sticky="w", pady=3)
        self.decode_image_label = tk.Label(decode_frame, text="No image selected", fg="gray", bg="#1e1e1e", font=self.font)
        self.decode_image_label.grid(row=0, column=2, sticky="w")
        tk.Label(decode_frame, text="Password:", fg=self.fg_color, bg="#1e1e1e", font=self.font).grid(row=1, column=0, sticky="w")
        self.decode_password = tk.Entry(decode_frame, width=35, show="*", bg=self.input_bg, fg=self.fg_color, insertbackground="white")
        self.decode_password.grid(row=1, column=1, sticky="w")
        tk.Button(decode_frame, text="🔓 Decode Message", command=self.thread_decode, bg="#4ec9b0", fg="black", font=self.font).grid(row=2, column=0, columnspan=2, pady=5)
        tk.Label(decode_frame, text="Decoded Message:", fg=self.fg_color, bg="#1e1e1e", font=self.font).grid(row=3, column=0, sticky="w", pady=(4,2))
        self.decoded_box = tk.Text(decode_frame, height=4, width=80, bg=self.input_bg, fg=self.fg_color, insertbackground="white", font=self.font)
        self.decoded_box.grid(row=4, column=0, columnspan=3, pady=5)

        # --- CLI-style progress bar ---
        self.canvas = tk.Canvas(root, width=700, height=25, bg="#2d2d2d", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.progress_rect = self.canvas.create_rectangle(0,0,0,25, fill="#4ec9b0", width=0)
        self.percentage_label = tk.Label(root, text="0%", fg="#4ec9b0", bg="#1e1e1e", font=self.font)
        self.percentage_label.place(x=360, y=root.winfo_height()-50)
        self.status_label = tk.Label(root, text="", fg="gray", bg="#1e1e1e", font=self.font)
        self.status_label.pack()

    # --- File selectors ---
    def select_encode_image(self):
        path = filedialog.askopenfilename(filetypes=[("PNG Images","*.png"),("All Files","*.*")])
        if path: self.input_image_encode = path; self.encode_image_label.config(text=os.path.basename(path), fg="#4ec9b0")

    def select_decode_image(self):
        path = filedialog.askopenfilename(filetypes=[("PNG Images","*.png"),("All Files","*.*")])
        if path: self.input_image_decode = path; self.decode_image_label.config(text=os.path.basename(path), fg="#4ec9b0")

    # --- Threaded encode/decode ---
    def thread_encode(self): threading.Thread(target=self.encode, daemon=True).start()
    def thread_decode(self): threading.Thread(target=self.decode, daemon=True).start()

    # --- Encode ---
    def encode(self):
        msg = self.message_entry.get("1.0","end").strip()
        pwd = self.password_entry.get().strip()
        out = self.output_entry.get().strip()
        if not msg or not pwd or not self.input_image_encode or not out:
            messagebox.showerror("Error","Fill all fields and select an image."); return
        try:
            self.update_status("Encrypting and embedding..."); self.update_progress(0)
            encrypted = encrypt_message(msg,pwd)
            embed_message_in_image(self.input_image_encode, encrypted, out, progress_callback=self.update_progress)
            messagebox.showinfo("Success",f"Message encoded and saved as {out}")
        except Exception as e: messagebox.showerror("Error",f"Encoding failed: {e}")
        finally: self.reset_status()

    # --- Decode ---
    def decode(self):
        pwd = self.decode_password.get().strip()
        if not pwd or not self.input_image_decode:
            messagebox.showerror("Error","Select image and enter password"); return
        try:
            self.update_status("Extracting hidden data..."); self.update_progress(0)
            encoded = extract_message_from_image(self.input_image_decode, progress_callback=self.update_progress)
            if not encoded: messagebox.showerror("Error","No hidden message found"); self.reset_status(); return
            self.update_status("Decrypting message...")
            message = decrypt_message(encoded,pwd)
            self.decoded_box.delete("1.0","end"); self.decoded_box.insert("end",message)
            self.update_status("Decoded successfully ✅"); self.update_progress(100)
        except Exception as e: messagebox.showerror("Error",f"Failed to decode: {e}")
        finally: self.reset_status()

    # --- GUI Updates ---
    def update_progress(self, val):
        self.canvas.coords(self.progress_rect, 0, 0, 7*val, 25)
        self.percentage_label.config(text=f"{int(val)}%")
        self.root.update_idletasks()
    def update_status(self,msg): self.status_label.config(text=msg); self.root.update_idletasks()
    def reset_status(self): self.root.after(1200, lambda:self.canvas.coords(self.progress_rect,0,0,0,25)); self.root.after(1200, lambda:self.percentage_label.config(text="0%")); self.root.after(1200, lambda:self.status_label.config(text=""))

if __name__=="__main__":
    root = tk.Tk()
    app = CLIApp(root)
    root.mainloop()




