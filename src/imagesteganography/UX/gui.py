#gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import hashlib
from datetime import datetime
import numpy as np

class Gui:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Image Steganography")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        #Zmienne
        self.current_image_path = None
        self.original_image = None
        self.processed_image = None
        self.encoded_image_path = None
        self.encryption_key = tk.StringVar(value="")
        self.add_noise_var = tk.BooleanVar(value=False)
        self.verify_message_var = tk.BooleanVar(value=True)
        self.image_capacity = 0
        self.psnr_value = 0
        
        self.bg_color = "#f0f0f0"
        self.primary_color = "#4a6fa5"
        self.secondary_color = "#166088"
        
        self.setup_styles()
        
        self.create_widgets()
        
        self.create_status_bar()
        
    def setup_styles(self):
        """Konfiguracja stylów"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Niestandardowe style
        style.configure('Title.TLabel', 
                       font=('Arial', 16, 'bold'),
                       background=self.bg_color)
        style.configure('Header.TLabel',
                       font=('Arial', 11, 'bold'),
                       background=self.bg_color)
        style.configure('Status.TLabel',
                       font=('Arial', 9),
                       background=self.primary_color,
                       foreground='white')
        
        # Przycisk akcentowy
        style.configure('Accent.TButton',
                       font=('Arial', 10, 'bold'),
                       background='#4CAF50',
                       foreground='white')
        
    def create_widgets(self):
        """Tworzenie wszystkich widżetów GUI"""
        #Glowny container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        #Grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        
        title_label = ttk.Label(main_container, 
                               text="🎨 Advanced Image Steganography",
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        #Lewy panel - Obrazy
        left_panel = ttk.LabelFrame(main_container, text="Image Preview", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)
        
        #Przyciski obrazow
        img_buttons_frame = ttk.Frame(left_panel)
        img_buttons_frame.grid(row=0, column=0, pady=(0, 10))
        
        ttk.Button(img_buttons_frame, text="📁 Load Image", 
                  command=self.load_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(img_buttons_frame, text="💾 Save Image", 
                  command=self.save_image).pack(side=tk.LEFT, padx=2)
        
        #Canvas dla obrazu
        self.image_canvas = tk.Canvas(left_panel, bg='white', width=300, height=250)
        self.image_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        #Placeholder obrazu
        self.image_canvas.create_text(150, 125, text="No image loaded\n\nClick 'Load Image'\nto select an image", 
                                     fill="gray", font=("Arial", 10), justify=tk.CENTER)
        
        #Info o obrazie
        self.image_info_label = ttk.Label(left_panel, text="No image loaded")
        self.image_info_label.grid(row=2, column=0, pady=10)
        
        #Srodkowy panel Operacje
        center_panel = ttk.LabelFrame(main_container, text="Steganography Operations", padding="10")
        center_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        center_panel.columnconfigure(0, weight=1)
        
        #Zakladki
        self.notebook = ttk.Notebook(center_panel)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        #Encode
        encode_frame = ttk.Frame(self.notebook, padding="5")
        self.create_encode_tab(encode_frame)
        self.notebook.add(encode_frame, text="🔒 Encode")
        
        #Decode
        decode_frame = ttk.Frame(self.notebook, padding="5")
        self.create_decode_tab(decode_frame)
        self.notebook.add(decode_frame, text="🔓 Decode")
        
        #Analyze
        analyze_frame = ttk.Frame(self.notebook, padding="5")
        self.create_analyze_tab(analyze_frame)
        self.notebook.add(analyze_frame, text="📊 Analyze")
        
        #Prawy panel - Info
        right_panel = ttk.LabelFrame(main_container, text="Information & Settings", padding="10")
        right_panel.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_panel.columnconfigure(0, weight=1)
        
        self.create_info_panel(right_panel)
        
        #Dolny panel - Log
        bottom_panel = ttk.LabelFrame(main_container, text="Activity Log", padding="10")
        bottom_panel.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        bottom_panel.columnconfigure(0, weight=1)
        bottom_panel.rowconfigure(0, weight=1)
        
        self.create_log_panel(bottom_panel)
        
    def create_encode_tab(self, parent):
        """Tworzenie zakładki Encode"""
        #Wiadomosc
        ttk.Label(parent, text="Message to hide:", style='Header.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.message_text = scrolledtext.ScrolledText(parent, width=40, height=8)
        self.message_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        #Przykladowa wiad
        example_msg = "This is a secret message that will be hidden in the image."
        self.message_text.insert("1.0", example_msg)
        
        #Szyfrowanie
        crypto_frame = ttk.LabelFrame(parent, text="Encryption", padding="5")
        crypto_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(crypto_frame, text="Encryption Key (AES):").grid(
            row=0, column=0, sticky=tk.W, padx=2)
        ttk.Entry(crypto_frame, textvariable=self.encryption_key, 
                 show="*", width=30).grid(row=0, column=1, padx=5)
        
        ttk.Button(crypto_frame, text="Generate Key", 
                  command=self.generate_key).grid(row=0, column=2, padx=5)
        
        #Opcje zaawansowane
        adv_frame = ttk.LabelFrame(parent, text="Advanced Options", padding="5")
        adv_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Checkbutton(adv_frame, text="Add noise for anti-forensic", 
                       variable=self.add_noise_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(adv_frame, text="Verify after encoding", 
                       variable=self.verify_message_var).grid(row=1, column=0, sticky=tk.W)
        
        
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="📥 Encode Message", 
                  command=self.encode_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_message).pack(side=tk.LEFT, padx=5)
        
    def create_decode_tab(self, parent):
        """Tworzenie zakładki Decode"""
        ttk.Label(parent, text="Load encoded image to extract message:", 
                 style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        #Przycisk ladowania
        ttk.Button(parent, text="📂 Load Encoded Image", 
                  command=self.load_encoded_image).grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        #Klucz deszyfrowania
        key_frame = ttk.Frame(parent)
        key_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(key_frame, text="Decryption Key:").pack(side=tk.LEFT)
        self.decode_key_entry = ttk.Entry(key_frame, show="*", width=30)
        self.decode_key_entry.pack(side=tk.LEFT, padx=5)
        
        #Wyswietlanie wiadomości
        ttk.Label(parent, text="Extracted Message:", 
                 style='Header.TLabel').grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        
        self.decoded_text = scrolledtext.ScrolledText(parent, width=40, height=10)
        self.decoded_text.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        #Przyciski
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="🔍 Decode Message", 
                  command=self.decode_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📋 Copy to Clipboard", 
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Save to File", 
                  command=self.save_decoded_message).pack(side=tk.LEFT, padx=5)
        
    def create_analyze_tab(self, parent):
        """Tworzenie zakładki Analyze"""
        #Pojemnosc
        capacity_frame = ttk.LabelFrame(parent, text="Image Capacity", padding="5")
        capacity_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.capacity_label = ttk.Label(capacity_frame, 
                                       text="Capacity: Not calculated")
        self.capacity_label.pack(anchor=tk.W)
        
        ttk.Button(capacity_frame, text="Calculate Capacity", 
                  command=self.calculate_capacity).pack(anchor=tk.W, pady=(5, 0))
        
        #PSNR
        psnr_frame = ttk.LabelFrame(parent, text="Image Quality (PSNR)", padding="5")
        psnr_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.psnr_label = ttk.Label(psnr_frame, text="PSNR: Not calculated")
        self.psnr_label.pack(anchor=tk.W)
        
        ttk.Button(psnr_frame, text="Calculate PSNR", 
                  command=self.calculate_psnr).pack(anchor=tk.W, pady=(5, 0))
        
        #Weryfikacja
        verify_frame = ttk.LabelFrame(parent, text="Message Verification", padding="5")
        verify_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.verify_label = ttk.Label(verify_frame, text="No verification performed")
        self.verify_label.pack(anchor=tk.W)
        
        ttk.Button(verify_frame, text="Verify Integrity", 
                  command=self.verify_integrity).pack(anchor=tk.W, pady=(5, 0))
        
        #Testy
        test_frame = ttk.LabelFrame(parent, text="Automated Tests", padding="5")
        test_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(test_frame, text="Run Complete Test (Encode → Decode → Compare)", 
                  command=self.run_complete_test).pack(anchor=tk.W)
        
    def create_info_panel(self, parent):
        """Tworzenie panelu informacyjnego"""
        #Informacje o projekcie
        info_text = """
        📋 Project Features:
        
        ✅ Basic Steganography (LSB)
        ✅ AES Encryption Support
        ✅ Multiple Formats: PNG, BMP, JPEG
        ✅ Image Capacity Calculation
        ✅ PSNR Quality Metric
        ✅ Anti-forensic Noise
        ✅ Message Verification
        ✅ Automated Testing
        
        Supported formats:
        • PNG (lossless)
        • BMP (uncompressed)
        • JPEG (with loss)
        • TIFF
        
        Instructions:
        1. Load an image
        2. Enter message to hide
        3. (Optional) Set encryption key
        4. Click Encode
        5. Save the encoded image
        """
        
        info_label = ttk.Label(parent, text=info_text, justify=tk.LEFT)
        info_label.grid(row=0, column=0, sticky=tk.W)
        
        #Separator
        ttk.Separator(parent, orient='horizontal').grid(
            row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        #Statystyki
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding="5")
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.stats_labels = {}
        stats = [
            ("Images Processed:", "0"),
            ("Messages Encoded:", "0"),
            ("Messages Decoded:", "0"),
            ("Successful Tests:", "0")
        ]
        
        for i, (text, value) in enumerate(stats):
            ttk.Label(stats_frame, text=text).grid(row=i, column=0, sticky=tk.W, pady=2)
            self.stats_labels[text] = ttk.Label(stats_frame, text=value)
            self.stats_labels[text].grid(row=i, column=1, sticky=tk.W, padx=10, pady=2)
        
    def create_log_panel(self, parent):
        """Tworzenie panelu logów"""
        self.log_text = scrolledtext.ScrolledText(parent, width=100, height=8)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        #Dodaj przykladowy log
        self.log("Application started")
        self.log("Ready to perform steganography operations")
        
        #Przyciski log
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))
        
        ttk.Button(button_frame, text="Clear Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Log", 
                  command=self.save_log).pack(side=tk.LEFT, padx=5)
        
    def create_status_bar(self):
        """Tworzenie status bara"""
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(self.status_bar, text="Ready", 
                                     foreground='white', background=self.primary_color)
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.format_label = ttk.Label(self.status_bar, text="", 
                                     foreground='white', background=self.primary_color)
        self.format_label.pack(side=tk.RIGHT, padx=10)
    
    
    def load_image(self):
        """Ładowanie obrazu - tylko GUI"""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select an image",
            filetypes=filetypes
        )
        
        if filename:
            try:
                self.current_image_path = filename
                self.original_image = Image.open(filename)
                
                #Wyswietlanie obrazu na canvasie
                self.display_image(self.original_image)
                
                #Aktualizacja informacji
                info = f"Loaded: {os.path.basename(filename)}\n"
                info += f"Size: {self.original_image.size[0]}x{self.original_image.size[1]}\n"
                info += f"Format: {self.original_image.format}"
                self.image_info_label.config(text=info)
                
                #Aktualizacja statusu
                self.update_status(f"Loaded: {os.path.basename(filename)}")
                self.format_label.config(text=f"Format: {self.original_image.format}")
                
                #Log
                self.log(f"Image loaded: {filename}")
                
                messagebox.showinfo("Success", f"Image loaded successfully!\n{info}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
                self.log(f"ERROR: Failed to load image")
    
    def display_image(self, image):
        """Wyświetlanie obrazu na canvasie"""
        #Czyszczenie canvasu
        self.image_canvas.delete("all")
        
        #Skalowanie
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        
        if canvas_width < 10:  #Default rozmiar
            canvas_width, canvas_height = 300, 250
        
        img_width, img_height = image.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        
        #Resize
        display_img = image.copy()
        display_img.thumbnail(new_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(display_img)
        
        #Rysowanie
        self.image_canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            image=photo, anchor=tk.CENTER
        )
        self.image_canvas.image = photo  #Keep reference
    
    def save_image(self):
        """Zapisywanie obrazu - tylko GUI"""
        if not self.processed_image:
            messagebox.showwarning("Warning", "No processed image to save!\nEncode a message first.")
            return
        
        messagebox.showinfo("Save Image", "This would save the processed image to a file.\n"
                          "Functionality to be implemented.")
        self.log("Save image clicked (not implemented yet)")
    
    def encode_message(self):
        """Kodowanie wiadomości - tylko GUI"""
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter a message to hide!")
            return
        
        #Symulacja kodowania
        messagebox.showinfo("Encoding", 
                          f"Message would be encoded using LSB method.\n"
                          f"Message length: {len(message)} characters\n"
                          f"Encryption: {'Yes' if self.encryption_key.get() else 'No'}\n"
                          f"Add noise: {'Yes' if self.add_noise_var.get() else 'No'}")
        
        
        self.update_status("Message encoded (simulated)")
        self.log(f"Encoding simulated - Message: '{message[:50]}...'")
        
        #Symulacja przetworzonego obrazu
        if self.original_image:
            self.processed_image = self.original_image.copy()
            self.display_image(self.processed_image)
            self.image_info_label.config(text="Image with hidden message (simulated)")
    
    def decode_message(self):
        """Dekodowanie wiadomości - tylko GUI"""
        if not self.encoded_image_path and not self.processed_image:
            messagebox.showwarning("Warning", "Please encode a message first or load encoded image!")
            return
        
        #Symulacja dekodowania
        simulated_message = "This is a simulated decoded message.\n" \
                          "In real implementation, this would be extracted from the image.\n" \
                          f"Encryption key used: {self.decode_key_entry.get() or 'None'}"
        
        
        self.decoded_text.delete("1.0", tk.END)
        self.decoded_text.insert("1.0", simulated_message)
        
        self.update_status("Message decoded (simulated)")
        self.log("Decoding simulated")
        
        messagebox.showinfo("Decoding", "Message decoded (simulated)")
    
    def load_encoded_image(self):
        """Ładowanie zakodowanego obrazu - tylko GUI"""
        filename = filedialog.askopenfilename(
            title="Select encoded image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.encoded_image_path = filename
                img = Image.open(filename)
                self.display_image(img)
                self.update_status(f"Loaded encoded image: {os.path.basename(filename)}")
                self.log(f"Encoded image loaded: {filename}")
                messagebox.showinfo("Success", "Encoded image loaded (simulated)")
            except:
                messagebox.showerror("Error", "Failed to load image")
    
    def calculate_capacity(self):
        """Obliczanie pojemności - tylko GUI"""
        if not self.original_image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        
        #Symulacja obliczen
        width, height = self.original_image.size
        capacity = width * height * 3 // 8  #Przykladowe obliczenie
        self.image_capacity = capacity
        
        self.capacity_label.config(
            text=f"Capacity: {capacity} bytes ({capacity} ASCII characters)"
        )
        self.update_status(f"Capacity calculated: {capacity} bytes")
        self.log(f"Capacity calculated: {capacity} bytes")
        
        messagebox.showinfo("Capacity", f"Image capacity: {capacity} bytes\n"
                          f"This is a simulated calculation.")
    
    def calculate_psnr(self):
        """Obliczanie PSNR - tylko GUI"""
        if not self.original_image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        
        
        self.psnr_value = 48.5  #Przykladowa wartosc
        quality = "Excellent" if self.psnr_value > 40 else "Good"
        
        self.psnr_label.config(
            text=f"PSNR: {self.psnr_value:.2f} dB ({quality} quality)"
        )
        self.update_status(f"PSNR calculated: {self.psnr_value:.2f} dB")
        self.log(f"PSNR calculated: {self.psnr_value:.2f} dB")
        
        messagebox.showinfo("PSNR", f"Peak Signal-to-Noise Ratio: {self.psnr_value:.2f} dB\n"
                          f"Quality: {quality}\n"
                          f"This is a simulated value.")
    
    def verify_integrity(self):
        """Weryfikacja integralności - tylko GUI"""
        if not self.encoded_image_path and not self.processed_image:
            messagebox.showwarning("Warning", "No encoded image to verify!")
            return
        
        #Symulacja weryfikacji
        self.verify_label.config(
            text="✓ Verification PASSED (simulated)",
            foreground="green"
        )
        self.update_status("Integrity verification passed")
        self.log("Integrity verification simulated - PASSED")
        
        messagebox.showinfo("Verification", "Message integrity verified successfully!\n"
                          "This is a simulated verification.")
    
    def run_complete_test(self):
        """Uruchomienie testu - tylko GUI"""
        messagebox.showinfo("Test", 
                          "Running complete test simulation:\n"
                          "1. Encode test message ✓\n"
                          "2. Decode message ✓\n"
                          "3. Compare results ✓\n\n"
                          "Test PASSED (simulated)")
        
        self.verify_label.config(
            text="✓ Complete test PASSED (simulated)",
            foreground="green"
        )
        self.update_status("Complete test executed")
        self.log("Complete test simulation - PASSED")
    
    def generate_key(self):
        """Generowanie klucza - tylko GUI"""
        import secrets
        import string
        
        #Generuj przykladowy klucz
        key = ''.join(secrets.choice(string.ascii_letters + string.digits) 
                     for _ in range(16))
        self.encryption_key.set(key)
        
        self.update_status("Encryption key generated")
        self.log("Encryption key generated")
        messagebox.showinfo("Key Generated", f"New encryption key:\n{key}")
    
    def clear_message(self):
        """Czyszczenie wiadomości"""
        self.message_text.delete("1.0", tk.END)
        self.update_status("Message cleared")
        self.log("Message input cleared")
    
    def copy_to_clipboard(self):
        """Kopiowanie do schowka - tylko GUI"""
        message = self.decoded_text.get("1.0", tk.END).strip()
        if message:
            self.root.clipboard_clear()
            self.root.clipboard_append(message)
            self.update_status("Message copied to clipboard (simulated)")
            self.log("Message copied to clipboard (simulated)")
            messagebox.showinfo("Clipboard", "Message copied to clipboard (simulated)")
        else:
            messagebox.showwarning("Warning", "No message to copy!")
    
    def save_decoded_message(self):
        """Zapisywanie wiadomości - tylko GUI"""
        message = self.decoded_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "No decoded message to save!")
            return
        
        messagebox.showinfo("Save Message", 
                          f"Message would be saved to a file.\n"
                          f"Length: {len(message)} characters\n\n"
                          f"This is a simulation.")
        self.log("Save decoded message clicked (simulated)")
    
    def update_status(self, message):
        """Aktualizacja status bara"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def log(self, message):
        """Dodawanie wpisu do logu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # Przewiń na dół
        self.log_text.update_idletasks()
    
    def clear_log(self):
        """Czyszczenie logu"""
        self.log_text.delete("1.0", tk.END)
        self.log("Log cleared")
        messagebox.showinfo("Log", "Log cleared")
    
    def save_log(self):
        """Zapisywanie logu - tylko GUI"""
        messagebox.showinfo("Save Log", "Log would be saved to a file.\nThis is a simulation.")
        self.log("Save log clicked (simulated)")

def run_gui():
    """Główna funkcja uruchamiająca aplikację"""
    root = tk.Tk()
    
    #Ustawienie ikony (opcjonalnie)
    try:
        #Mozna dodac plik icon.ico do folderu projektu
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = Gui(root)
    
    #Zamkniecie
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
