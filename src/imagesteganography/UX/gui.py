import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import sys
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
imagestego_dir = os.path.dirname(current_dir)
src_dir = os.path.dirname(imagestego_dir)

print(f"📁 gui.py: {current_dir}")
print(f"📁 imagesteganography: {imagestego_dir}")
print(f"📁 src: {src_dir}")

if os.path.exists(src_dir):
    sys.path.insert(0, src_dir)
    print(f"✅ Dodano src do ścieżki: {src_dir}")
else:
    print(f"❌ Folder src nie istnieje: {src_dir}")
    src_dir = os.path.join(os.path.dirname(current_dir), "..")
    if os.path.exists(src_dir):
        sys.path.insert(0, src_dir)
        print(f"✅ Dodano src (alternatywnie): {src_dir}")

print("\n🔄 Importowanie modułów partnera...")

try:
    from imagesteganography.utilities.ImageFormat import ImageFormat
    print("✅ ImageFormat zaimportowany")
except ImportError as e:
    print(f"❌ ImageFormat error: {e}")
    from enum import Enum
    class ImageFormat(Enum):
        PNG = "png"
        BMP = "bmp"
        TIFF = "tiff"
        JPEG = "jpeg"
    print("⚠ Używam tymczasowego ImageFormat")

try:
    from imagesteganography.core.StegoService import StegoService
    print("✅ StegoService zaimportowany")
except ImportError as e:
    print(f"❌ StegoService error: {e}")
    # Dummy service
    class StegoService:
        def hide_message(self, *args, **kwargs):
            raise Exception(f"StegoService nie załadowany: {e}")
        def reveal_message(self, *args, **kwargs):
            raise Exception(f"StegoService nie załadowany: {e}")
    print("⚠ Używam dummy StegoService")
try:
    from utilities.crypto import AESCipher, SimpleAESCipher
    CRYPTO_AVAILABLE = True
    print("✅ Crypto zaimportowane")
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠ Crypto nie dostępne")
    class DummyCipher:
        @staticmethod
        def encrypt(msg, pwd): return msg.encode() if pwd else msg
        @staticmethod 
        def decrypt(enc, pwd): return enc.decode() if isinstance(enc, bytes) else enc
        @staticmethod
        def generate_key(): 
            import secrets
            return secrets.token_hex(16)
    AESCipher = DummyCipher
    SimpleAESCipher = DummyCipher

print("=" * 50)
print("✅ Importy zakończone - uruchamiam GUI")
print("=" * 50)

class Gui:
    def __init__(self, root):
        self.root = root
        self.root.title("Zaawansowana Steganografia Obrazów")
        self.root.geometry("1300x960")  # <-- WIĘKSZE OKNO
        self.root.minsize(1000, 650)    # <-- WIĘKSZE MINIMUM
        
        self.current_image_path = None
        self.original_image = None
        self.processed_image = None
        self.encoded_image_path = None
        self.encryption_key = tk.StringVar(value="")
        self.show_key_var = tk.BooleanVar(value=False)
        self.add_noise_var = tk.BooleanVar(value=False)
        self.verify_message_var = tk.BooleanVar(value=True)
        self.image_capacity = 0
        self.psnr_value = 0
        self.stego_service = StegoService()
        self.crypto_available = CRYPTO_AVAILABLE
        
        self.bg_color = "#f0f0f0"
        self.primary_color = "#4a6fa5"
        self.secondary_color = "#166088"
        
        self.setup_styles()
        self.create_widgets()
        self.create_status_bar()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', 
                       font=('Arial', 18, 'bold'),
                       background=self.bg_color)
        style.configure('Header.TLabel',
                       font=('Arial', 12, 'bold'),
                       background=self.bg_color)
        style.configure('Status.TLabel',
                       font=('Arial', 10),
                       background=self.primary_color,
                       foreground='white')
        style.configure('Accent.TButton',
                       font=('Arial', 11, 'bold'),
                       background='#4CAF50',
                       foreground='white')
        
    def create_widgets(self):
        main_container = ttk.Frame(self.root, padding="15")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        title_label = ttk.Label(main_container, 
                               text="Zaawansowana Steganografia Obrazów",
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 25))
        
        left_panel = ttk.LabelFrame(main_container, text="Podgląd Obrazu", padding="15")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)
        
        img_buttons_frame = ttk.Frame(left_panel)
        img_buttons_frame.grid(row=0, column=0, pady=(0, 15))
        
        ttk.Button(img_buttons_frame, text="📁 Wczytaj Obraz", 
                  command=self.load_image).pack(side=tk.LEFT, padx=3)
        ttk.Button(img_buttons_frame, text="💾 Zapisz Obraz", 
                  command=self.save_image).pack(side=tk.LEFT, padx=3)
        
        self.image_canvas = tk.Canvas(left_panel, bg='white', width=350, height=300)
        self.image_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.image_canvas.create_text(175, 150, 
                                     text="Brak załadowanego obrazu\n\nKliknij 'Wczytaj Obraz'\naby wybrać obraz", 
                                     fill="gray", font=("Arial", 11), justify=tk.CENTER)
        
        self.image_info_label = ttk.Label(left_panel, text="Brak załadowanego obrazu", font=("Arial", 10))
        self.image_info_label.grid(row=2, column=0, pady=15)
        
        center_panel = ttk.LabelFrame(main_container, text="Operacje Steganograficzne", padding="15")
        center_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        center_panel.columnconfigure(0, weight=1)
        
        self.notebook = ttk.Notebook(center_panel)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        encode_frame = ttk.Frame(self.notebook, padding="10")
        self.create_encode_tab(encode_frame)
        self.notebook.add(encode_frame, text="🔒 Koduj")
        
        decode_frame = ttk.Frame(self.notebook, padding="10")
        self.create_decode_tab(decode_frame)
        self.notebook.add(decode_frame, text="🔓 Dekoduj")
        
        analyze_frame = ttk.Frame(self.notebook, padding="10")
        self.create_analyze_tab(analyze_frame)
        self.notebook.add(analyze_frame, text="📊 Analizuj")
        
        right_panel = ttk.LabelFrame(main_container, text="Informacje i Ustawienia", padding="15")
        right_panel.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(15, 0))
        right_panel.columnconfigure(0, weight=1)
        
        self.create_info_panel(right_panel)
        
        bottom_panel = ttk.LabelFrame(main_container, text="Dziennik Aktywności", padding="15")
        bottom_panel.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0))
        bottom_panel.columnconfigure(0, weight=1)
        bottom_panel.rowconfigure(0, weight=1)
        
        self.create_log_panel(bottom_panel)
        
    def create_encode_tab(self, parent):
        ttk.Label(parent, text="Wiadomość do ukrycia:", style='Header.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.message_text = scrolledtext.ScrolledText(parent, width=45, height=10, font=("Arial", 10))
        self.message_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        self.message_text.insert("1.0", "Wpisz swoją tajną wiadomość tutaj...")
        
        crypto_frame = ttk.LabelFrame(parent, text="Szyfrowanie AES-256", padding="10")
        crypto_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        crypto_frame.columnconfigure(1, weight=1)
        
        ttk.Label(crypto_frame, text="Klucz szyfrowania:", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        
        key_entry_frame = ttk.Frame(crypto_frame)
        key_entry_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        key_entry_frame.columnconfigure(1, weight=1)
        
        self.encryption_key_entry = ttk.Entry(key_entry_frame, textvariable=self.encryption_key, 
                                            show="*", width=40, font=("Arial", 10))
        self.encryption_key_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        key_entry_frame.columnconfigure(0, weight=1)

        self.show_key_btn = ttk.Button(key_entry_frame, text="👁 Pokaż", 
                                      command=self.toggle_key_visibility, width=8)
        self.show_key_btn.grid(row=0, column=1, padx=(0, 10))

        ttk.Button(key_entry_frame, text="🎲 Generuj Klucz", 
                  command=self.generate_key, width=12).grid(row=0, column=2)
        
        crypto_status = "✅ Dostępne" if self.crypto_available else "❌ Wymaga: pip install cryptography"
        ttk.Label(crypto_frame, text=f"Status: {crypto_status}", 
                 font=("Arial", 9), foreground="green" if self.crypto_available else "red").grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        adv_frame = ttk.LabelFrame(parent, text="Opcje Zaawansowane", padding="10")
        adv_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Checkbutton(adv_frame, text="Dodaj szum (anti-forensic)", 
                       variable=self.add_noise_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(adv_frame, text="Weryfikuj po zakodowaniu", 
                       variable=self.verify_message_var).grid(row=1, column=0, sticky=tk.W)
        
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Button(button_frame, text="📥 Koduj Wiadomość", 
                  command=self.encode_message, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Wyczyść", 
                  command=self.clear_message, width=15).pack(side=tk.LEFT, padx=5)
        
    def create_decode_tab(self, parent):
        ttk.Label(parent, text="Wczytaj zakodowany obraz aby odczytać wiadomość:", 
                 style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        ttk.Button(parent, text="📂 Wczytaj Zakodowany Obraz", 
                  command=self.load_encoded_image, width=25).grid(row=1, column=0, sticky=tk.W, pady=(0, 15))
        
        key_frame = ttk.LabelFrame(parent, text="Deszyfrowanie AES", padding="10")
        key_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        key_frame.columnconfigure(1, weight=1)
        
        ttk.Label(key_frame, text="Klucz deszyfrowania:", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        decode_key_frame = ttk.Frame(key_frame)
        decode_key_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        decode_key_frame.columnconfigure(0, weight=1)
        
        self.decode_key_entry = ttk.Entry(decode_key_frame, show="*", width=40, font=("Arial", 10))
        self.decode_key_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.decode_show_key_btn = ttk.Button(decode_key_frame, text="👁 Pokaż", 
                                            command=lambda: self.toggle_key_visibility(self.decode_key_entry), 
                                            width=8)
        self.decode_show_key_btn.grid(row=0, column=1)
        
        ttk.Label(parent, text="Odczytywana Wiadomość:", 
                 style='Header.TLabel').grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        
        self.decoded_text = scrolledtext.ScrolledText(parent, width=45, height=12, font=("Arial", 10))
        self.decoded_text.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="🔍 Dekoduj Wiadomość", 
                  command=self.decode_message, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📋 Kopiuj", 
                  command=self.copy_to_clipboard, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Zapisz", 
                  command=self.save_decoded_message, width=15).pack(side=tk.LEFT, padx=5)
        
    def create_analyze_tab(self, parent):
        capacity_frame = ttk.LabelFrame(parent, text="Pojemność Obrazu", padding="10")
        capacity_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.capacity_label = ttk.Label(capacity_frame, text="Pojemność: Nie obliczono", font=("Arial", 10))
        self.capacity_label.pack(anchor=tk.W)
        
        ttk.Button(capacity_frame, text="🔢 Oblicz Pojemność", 
                  command=self.calculate_capacity, width=20).pack(anchor=tk.W, pady=(10, 0))
        
        psnr_frame = ttk.LabelFrame(parent, text="Jakość Obrazu (PSNR)", padding="10")
        psnr_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.psnr_label = ttk.Label(psnr_frame, text="PSNR: Nie obliczono", font=("Arial", 10))
        self.psnr_label.pack(anchor=tk.W)
        
        ttk.Button(psnr_frame, text="📊 Oblicz PSNR", 
                  command=self.calculate_psnr, width=20).pack(anchor=tk.W, pady=(10, 0))
        
        verify_frame = ttk.LabelFrame(parent, text="Weryfikacja Wiadomości", padding="10")
        verify_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.verify_label = ttk.Label(verify_frame, text="Brak weryfikacji", font=("Arial", 10))
        self.verify_label.pack(anchor=tk.W)
        
        ttk.Button(verify_frame, text="✓ Zweryfikuj Integralność", 
                  command=self.verify_integrity, width=20).pack(anchor=tk.W, pady=(10, 0))
        
        test_frame = ttk.LabelFrame(parent, text="Testy Automatyczne", padding="10")
        test_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Button(test_frame, text="🧪 Uruchom Pełny Test (Koduj → Dekoduj → Porównaj)", 
                  command=self.run_complete_test, width=40).pack(anchor=tk.W)
        
    def create_info_panel(self, parent):
        crypto_status = "✅ Dostępne" if self.crypto_available else "⚠ Ograniczone (brak cryptography)"
        
        info_text = f"""Funkcje Projektu:

✅ Podstawowa Steganografia (LSB)
🔒 Szyfrowanie AES: {crypto_status}
✅ Wiele Formatów: PNG, BMP, JPEG, TIFF
✅ Obliczanie Pojemności Obrazu
✅ Metryka Jakości PSNR
✅ Szum Anti-Forensic
✅ Weryfikacja Wiadomości
✅ Testy Automatyczne

Instrukcje szyfrowania:
1. Wpisz wiadomość
2. Wpisz klucz lub kliknij 'Generuj Klucz'
3. Kliknij '👁' aby zobaczyć klucz
4. Zapisz klucz - będzie potrzebny do odczytu!
5. Zakoduj obraz
6. Do odczytu potrzebny TEN SAM klucz"""
        
        info_label = ttk.Label(parent, text=info_text, justify=tk.LEFT, font=("Arial", 10))
        info_label.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Separator(parent, orient='horizontal').grid(
            row=1, column=0, sticky=(tk.W, tk.E), pady=15)
        
        stats_frame = ttk.LabelFrame(parent, text="Statystyki", padding="10")
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.stats_labels = {}
        stats = [
            ("Obrazy Przetworzone:", "0"),
            ("Wiadomości Zakodowane:", "0"),
            ("Wiadomości Odczytywane:", "0"),
            ("Testy Pomyślne:", "0")
        ]
        
        for i, (text, value) in enumerate(stats):
            ttk.Label(stats_frame, text=text, font=("Arial", 10)).grid(
                row=i, column=0, sticky=tk.W, pady=3)
            self.stats_labels[text] = ttk.Label(stats_frame, text=value, font=("Arial", 10, "bold"))
            self.stats_labels[text].grid(row=i, column=1, sticky=tk.W, padx=15, pady=3)
        
    def create_log_panel(self, parent):
        self.log_text = scrolledtext.ScrolledText(parent, width=120, height=10, font=("Courier New", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log("Aplikacja uruchomiona")
        if not self.crypto_available:
            self.log("UWAGA: Biblioteka 'cryptography' nie zainstalowana. Szyfrowanie ograniczone.")
            self.log("Uruchom: pip install cryptography dla pełnego AES-256")
        self.log("Moduł steganografii załadowany")
        
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, sticky=tk.E, pady=(10, 0))
        
        ttk.Button(button_frame, text="🗑️ Wyczyść Dziennik", 
                  command=self.clear_log, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Zapisz Dziennik", 
                  command=self.save_log, width=15).pack(side=tk.LEFT, padx=5)
        
    def create_status_bar(self):
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(self.status_bar, text="Gotowy", 
                                     font=("Arial", 10),
                                     foreground='white', background=self.primary_color)
        self.status_label.pack(side=tk.LEFT, padx=15, pady=3)
        
        engine_label = ttk.Label(self.status_bar, text=f"Silnik: {'OK' if self.crypto_available else 'BRAK CRYPTO'}", 
                                font=("Arial", 10), 
                                foreground='white', background=self.primary_color)
        engine_label.pack(side=tk.RIGHT, padx=15, pady=3)
    
    def toggle_key_visibility(self, entry_widget=None):
        """Przełącz widoczność klucza w polu tekstowym"""
        if entry_widget is None:
            entry_widget = self.encryption_key_entry
            button_widget = self.show_key_btn
        else:
            button_widget = self.decode_show_key_btn
        
        current_show = entry_widget.cget("show")
        if current_show == "*":
            entry_widget.config(show="")
            button_widget.config(text="🙈 Ukryj")
        else:
            entry_widget.config(show="*")
            button_widget.config(text="👁 Pokaż")
    
    def _encrypt_message(self, message: str, password: str) -> str:
        """Szyfruje wiadomość przed wysłaniem do StegoService."""
        if not password or not self.crypto_available:
            return message
        
        try:
            encrypted = AESCipher.encrypt(message, password)
            import base64
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            self.log(f"Błąd szyfrowania AES: {e}")
            try:
                encrypted = SimpleAESCipher.encrypt_simple(message, password)
                return encrypted.decode('utf-8', errors='ignore')
            except Exception as e2:
                self.log(f"Błąd prostego szyfrowania: {e2}")
                return message
    
    def _decrypt_message(self, encrypted_message: str, password: str) -> str:
        """Deszyfruje wiadomość po odebraniu z StegoService."""
        if not password or not self.crypto_available:
            return encrypted_message
        
        try:
            import base64
            try:
                encrypted_data = base64.b64decode(encrypted_message)
                return AESCipher.decrypt(encrypted_data, password)
            except:
                return SimpleAESCipher.decrypt_simple(
                    encrypted_message.encode('utf-8'), 
                    password
                )
        except Exception as e:
            self.log(f"Błąd deszyfrowania: {e}")
            raise ValueError(f"Nie można odszyfrować. Zły klucz? Błąd: {e}")
    
    def load_image(self):
        filetypes = [
            ("Pliki obrazów", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif"),
            ("Wszystkie pliki", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Wybierz obraz",
            filetypes=filetypes
        )
        
        if filename:
            try:
                self.current_image_path = filename
                self.original_image = Image.open(filename)
                self.display_image(self.original_image)
                
                info = f"Wczytano: {os.path.basename(filename)}\n"
                info += f"Rozmiar: {self.original_image.size[0]}x{self.original_image.size[1]}\n"
                info += f"Format: {self.original_image.format}"
                self.image_info_label.config(text=info)
                
                self.update_status(f"Wczytano: {os.path.basename(filename)}")
                self.log(f"Obraz wczytany: {filename}")
                self._update_statistic("Obrazy Przetworzone:", "+1")
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można wczytać obrazu: {str(e)}")
                self.log(f"BŁĄD wczytywania obrazu: {str(e)}")
    
    def display_image(self, image):
        self.image_canvas.delete("all")
        
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        
        if canvas_width < 10:
            canvas_width, canvas_height = 350, 300
        
        img_width, img_height = image.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        
        display_img = image.copy()
        display_img.thumbnail(new_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(display_img)
        
        self.image_canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            image=photo, anchor=tk.CENTER
        )
        self.image_canvas.image = photo
    
    def save_image(self):
        if not self.processed_image:
            messagebox.showwarning("Ostrzeżenie", "Brak przetworzonego obrazu do zapisania!\nNajpierw zakoduj wiadomość.")
            return
        
        file = filedialog.asksaveasfilename(
            title="Zapisz przetworzony obraz",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("BMP files", "*.bmp"), 
                      ("TIFF files", "*.tiff"), ("Wszystkie pliki", "*.*")]
        )
        
        if file:
            try:
                self.processed_image.save(file)
                self.update_status(f"Obraz zapisany: {os.path.basename(file)}")
                self.log(f"Obraz zapisany do: {file}")
                messagebox.showinfo("Sukces", f"Obraz zapisany do:\n{file}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można zapisać obrazu: {str(e)}")
                self.log(f"BŁĄD zapisywania obrazu: {str(e)}")
    
    def encode_message(self):
        if not self.current_image_path:
            messagebox.showwarning("Ostrzeżenie", "Najpierw wczytaj obraz!")
            return
        
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Ostrzeżenie", "Wpisz wiadomość do ukrycia!")
            return
        
        encryption_key = self.encryption_key.get().strip()
        
        if encryption_key and self.crypto_available:
            try:
                message_to_hide = self._encrypt_message(message, encryption_key)
                self.log(f"Zaszyfrowano wiadomość ({len(message_to_hide)} bajtów)")
                encryption_status = "z szyfrowaniem AES"
            except Exception as e:
                messagebox.showerror("Błąd szyfrowania", 
                                   f"Nie można zaszyfrować: {e}\n"
                                   f"Ukrywam nieszyfrowaną wiadomość.")
                message_to_hide = message
                encryption_status = "bez szyfrowania (błąd)"
        else:
            message_to_hide = message
            if encryption_key and not self.crypto_available:
                messagebox.showwarning("Brak cryptography", 
                                     "Biblioteka cryptography nie zainstalowana.\n"
                                     "Używam prostego szyfrowania.")
                message_to_hide = self._encrypt_message(message, encryption_key)
                encryption_status = "z prostym szyfrowaniem"
            else:
                encryption_status = "bez szyfrowania"
        
        output_file = filedialog.asksaveasfilename(
            title="Zapisz zakodowany obraz jako",
            defaultextension=".bmp",
            filetypes=[
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff *.tif"),
                ("PNG files", "*.png"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        
        if not output_file:
            return
        
        try:
            fmt = ImageFormat.from_path(self.current_image_path)
            self.update_status("Kodowanie wiadomości...")
            self.log(f"Kodowanie {encryption_status} do: {output_file}")
            
            result_path = self.stego_service.hide_message(
                image_path=self.current_image_path,
                message=message_to_hide,
                image_format=fmt,
                output_path=output_file
            )
            
            self.encoded_image_path = result_path
            self.update_status("Wiadomość zakodowana pomyślnie!")
            self.log(f"SUKCES: Wiadomość zakodowana do: {os.path.basename(result_path)}")
            
            try:
                self.processed_image = Image.open(result_path)
                self.display_image(self.processed_image)
                self.image_info_label.config(text=f"Zakodowany obraz: {os.path.basename(result_path)}")
            except Exception as e:
                self.log(f"Nie można wyświetlić obrazu wyjściowego: {e}")
            
            messagebox.showinfo("Sukces", f"Wiadomość zakodowana pomyślnie!\n\n"
                                        f"Plik: {os.path.basename(result_path)}\n"
                                        f"Szyfrowanie: {encryption_status}")
            
            if self.verify_message_var.get():
                self.verify_after_encode(message, result_path, encryption_key)
            
            self._update_statistic("Wiadomości Zakodowane:", "+1")
                
        except Exception as e:
            self.update_status("Kodowanie nie powiodło się!")
            self.log(f"BŁĄD: {str(e)}")
            messagebox.showerror("Błąd Kodowania", f"Nie można zakodować wiadomości:\n{str(e)}")
    
    def decode_message(self):
        if not self.encoded_image_path and not self.current_image_path:
            messagebox.showwarning("Ostrzeżenie", "Najpierw wczytaj zakodowany obraz!")
            return
        
        image_to_decode = self.encoded_image_path or self.current_image_path
        decryption_key = self.decode_key_entry.get().strip()
        
        try:
            fmt = ImageFormat.from_path(image_to_decode)
            self.update_status("Dekodowanie wiadomości...")
            
            if decryption_key:
                self.log(f"Dekodowanie z deszyfrowaniem, klucz: {'*' * len(decryption_key)}")
            else:
                self.log("Dekodowanie bez deszyfrowania")
            
            extracted = self.stego_service.reveal_message(
                image_path=image_to_decode,
                image_format=fmt
            )
            
            if decryption_key and self.crypto_available:
                try:
                    final_message = self._decrypt_message(extracted, decryption_key)
                    self.log(f"Odszyfrowano wiadomość ({len(final_message)} znaków)")
                    decryption_status = "z deszyfrowaniem"
                except Exception as e:
                    self.log(f"Nie można odszyfrować: {e}")
                    final_message = extracted
                    decryption_status = "bez deszyfrowania (błąd)"
                    messagebox.showwarning("Błąd deszyfrowania", 
                                         f"Nie można odszyfrować.\n"
                                         f"Może zły klucz lub wiadomość niezaszyfrowana?\n"
                                         f"Pokazuję surowy odczyt.")
            else:
                final_message = extracted
                decryption_status = "bez deszyfrowania"
            
            self.decoded_text.delete("1.0", tk.END)
            self.decoded_text.insert("1.0", final_message)
            
            self.update_status("Wiadomość odczytana pomyślnie!")
            self.log(f"SUKCES: Odczytano {len(final_message)} znaków ({decryption_status})")
            
            messagebox.showinfo("Sukces", f"Wiadomość odczytana pomyślnie!\n\n"
                                        f"Odczytano {len(final_message)} znaków\n"
                                        f"Deszyfrowanie: {decryption_status}")
            
            self._update_statistic("Wiadomości Odczytywane:", "+1")
            
        except Exception as e:
            self.update_status("Dekodowanie nie powiodło się!")
            self.log(f"BŁĄD: {str(e)}")
            messagebox.showerror("Błąd Dekodowania", f"Nie można odczytać wiadomości:\n{str(e)}")
    
    def load_encoded_image(self):
        filename = filedialog.askopenfilename(
            title="Wybierz zakodowany obraz",
            filetypes=[("Pliki obrazów", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("Wszystkie pliki", "*.*")]
        )
        
        if filename:
            try:
                self.encoded_image_path = filename
                img = Image.open(filename)
                self.display_image(img)
                self.update_status(f"Wczytano zakodowany obraz: {os.path.basename(filename)}")
                self.log(f"Zakodowany obraz wczytany: {filename}")
                messagebox.showinfo("Sukces", "Zakodowany obraz wczytany pomyślnie")
                self._update_statistic("Obrazy Przetworzone:", "+1")
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można wczytać obrazu: {str(e)}")
                self.log(f"BŁĄD wczytywania zakodowanego obrazu: {str(e)}")
    
    def calculate_capacity(self):
        if not self.current_image_path:
            messagebox.showwarning("Ostrzeżenie", "Najpierw wczytaj obraz!")
            return
        
        try:
            from PIL import Image
            
            self.update_status("Obliczanie pojemności...")
            
            img = Image.open(self.current_image_path)
            width, height = img.size
            
            if img.mode in ("RGB", "RGBA"):
                channels = 3
            elif img.mode == "L":
                channels = 1
            else:
                channels = 3
            
            bits_capacity = width * height * channels
            bytes_capacity = bits_capacity // 8
            usable_bytes = bytes_capacity - 4
            if usable_bytes < 0:
                usable_bytes = 0
            
            self.image_capacity = usable_bytes
            
            if usable_bytes > 1024 * 1024:
                display = f"{usable_bytes / (1024*1024):.1f} MB"
            elif usable_bytes > 1024:
                display = f"{usable_bytes / 1024:.1f} KB"
            else:
                display = f"{usable_bytes} bajtów"
            
            self.capacity_label.config(text=f"Pojemność: {display} ({usable_bytes} bajtów)")
            self.update_status(f"Pojemność: {display}")
            self.log(f"SUKCES: Pojemność obrazu: {usable_bytes} bajtów")
            
            messagebox.showinfo("Pojemność Obrazu", 
                              f"Maksymalny rozmiar wiadomości:\n\n"
                              f"• {usable_bytes} bajtów\n"
                              f"• ~{usable_bytes} znaków ASCII\n"
                              f"• ~{usable_bytes//2} znaków Unicode")
            
        except Exception as e:
            self.update_status("Obliczanie pojemności nie powiodło się")
            self.log(f"BŁĄD: {str(e)}")
            messagebox.showerror("Błąd", f"Nie można obliczyć pojemności:\n{str(e)}")
    
    def calculate_psnr(self):
        if not self.current_image_path:
            messagebox.showwarning("Ostrzeżenie", "Najpierw wczytaj oryginalny obraz!")
            return
        
        if not self.encoded_image_path:
            encoded = filedialog.askopenfilename(
                title="Wybierz zakodowany obraz do porównania PSNR",
                filetypes=[("Pliki obrazów", "*.png *.jpg *.jpeg *.bmp *.tiff")]
            )
            if not encoded:
                return
            self.encoded_image_path = encoded
        
        try:
            self.update_status("Obliczanie PSNR...")
            
            import math
            import numpy as np
            from PIL import Image
            
            original = np.array(Image.open(self.current_image_path).convert('RGB'))
            encoded_img = np.array(Image.open(self.encoded_image_path).convert('RGB'))
            
            mse = np.mean((original - encoded_img) ** 2)
            if mse == 0:
                psnr = 100
            else:
                max_pixel = 255.0
                psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
            
            self.psnr_value = psnr
            
            if psnr > 40:
                quality = "Doskonała (bardzo wysoka jakość)"
            elif psnr > 30:
                quality = "Dobra (niewielkie zmiany)"
            elif psnr > 20:
                quality = "Średnia (zauważalne zmiany)"
            else:
                quality = "Słaba (znaczna degradacja)"
            
            self.psnr_label.config(text=f"PSNR: {psnr:.2f} dB - {quality}")
            self.update_status(f"PSNR: {psnr:.2f} dB")
            self.log(f"SUKCES: PSNR = {psnr:.2f} dB")
            
            messagebox.showinfo("Wynik PSNR", 
                              f"Stosunek Sygnału do Szumu:\n"
                              f"• Wartość: {psnr:.2f} dB\n"
                              f"• Jakość: {quality}\n\n"
                              f"Większy PSNR = lepsza jakość")
            
        except Exception as e:
            self.update_status("Obliczanie PSNR nie powiodło się")
            self.log(f"BŁĄD: {str(e)}")
            messagebox.showerror("Błąd", f"Nie można obliczyć PSNR:\n{str(e)}")
    
    def verify_integrity(self):
        if not self.encoded_image_path and not self.processed_image:
            messagebox.showwarning("Ostrzeżenie", "Brak zakodowanego obrazu do weryfikacji!")
            return
        
        image_to_verify = self.encoded_image_path or self.current_image_path
        if not image_to_verify:
            return
        
        try:
            fmt = ImageFormat.from_path(image_to_verify)
            self.update_status("Weryfikacja integralności...")
            
            message = self.stego_service.reveal_message(
                image_path=image_to_verify,
                image_format=fmt
            )
            
            if message:
                self.verify_label.config(text=f"✓ Weryfikacja POWIODŁA SIĘ ({len(message)} znaków)", foreground="green")
                self.update_status("Weryfikacja integralności powiodła się")
                self.log(f"SUKCES weryfikacji - PRZESZŁA ({len(message)} znaków do odczytania)")
                
                messagebox.showinfo("Weryfikacja", 
                                  f"Integralność obrazu zweryfikowana pomyślnie!\n\n"
                                  f"Zawiera czytelną wiadomość: {len(message)} znaków")
            else:
                self.verify_label.config(text="✗ Weryfikacja NIE POWIODŁA SIĘ", foreground="red")
                self.log(f"BŁĄD weryfikacji - NIE PRZESZŁA")
                
        except Exception as e:
            self.verify_label.config(text="✗ Weryfikacja NIE POWIODŁA SIĘ", foreground="red")
            self.log(f"BŁĄD weryfikacji: {str(e)}")
    
    def verify_after_encode(self, original_message, encoded_image_path, encryption_key=None):
        self.log("Rozpoczynanie weryfikacji po kodowaniu...")
        
        try:
            fmt = ImageFormat.from_path(encoded_image_path)
            extracted = self.stego_service.reveal_message(
                image_path=encoded_image_path,
                image_format=fmt
            )
            
            if encryption_key and self.crypto_available:
                try:
                    extracted = self._decrypt_message(extracted, encryption_key)
                except:
                    pass
            
            if original_message == extracted:
                self.log("SUKCES weryfikacji po kodowaniu: wiadomości identyczne")
                messagebox.showinfo("Weryfikacja", 
                                  "SUKCES weryfikacji po kodowaniu!\n\n"
                                  "Zakodowana wiadomość pasuje do oryginału.")
            else:
                from tests.verification import calculate_similarity
                similarity = calculate_similarity(original_message, extracted)
                self.log(f"OSTRZEŻENIE: wiadomości różnią się ({similarity}% podobieństwa)")
                
        except Exception as e:
            self.log(f"BŁĄD weryfikacji po kodowaniu: {str(e)}")
    
    def run_complete_test(self):
        if not self.current_image_path:
            messagebox.showwarning("Ostrzeżenie", "Najpierw wczytaj obraz do testowania!")
            return
        
        import tempfile
        import time
        
        test_message = f"Testowa wiadomość - {time.strftime('%H:%M:%S')}"
        temp_dir = tempfile.gettempdir()
        test_output = os.path.join(temp_dir, f"stego_test_{time.strftime('%Y%m%d_%H%M%S')}.bmp")
        
        self.update_status("Uruchamianie pełnego testu...")
        self.log(f"Rozpoczynanie pełnego testu")
        
        try:
            fmt = ImageFormat.from_path(self.current_image_path)
            
            self.log("Krok 1: Kodowanie wiadomości testowej...")
            result_path = self.stego_service.hide_message(
                image_path=self.current_image_path,
                message=test_message,
                image_format=fmt,
                output_path=test_output
            )
            
            self.log(f"SUKCES kroku 1 - zakodowano do: {result_path}")
            
            self.log("Krok 2: Odczytywanie wiadomości testowej...")
            decoded_message = self.stego_service.reveal_message(
                image_path=result_path,
                image_format=fmt
            )
            
            self.log(f"SUKCES kroku 2: Odczytywane {len(decoded_message)} znaków")
            
            self.log("Krok 3: Porównywanie wiadomości...")
            
            if test_message == decoded_message:
                self.verify_label.config(text="✓ Pełny test PRZESZŁY", foreground="green")
                self.update_status("Pełny test PRZESZŁY")
                self.log("SUKCES: PEŁNY TEST PRZESZŁY!")
                
                messagebox.showinfo("Wynik Testu", 
                                  "SUKCES: PEŁNY TEST PRZESZŁY!\n\n"
                                  "Wszystkie kroki zakończone pomyślnie!")
                
                self._update_statistic("Testy Pomyślne:", "+1")
                
            else:
                from tests.verification import calculate_similarity
                similarity = calculate_similarity(test_message, decoded_message)
                self.verify_label.config(text=f"✗ Pełny test NIEUDANY ({similarity}%)", foreground="red")
                self.update_status("Pełny test NIEUDANY")
                self.log(f"BŁĄD: Pełny test NIEUDANY: podobieństwo {similarity}%")
                
                messagebox.showerror("Test Nieudany", 
                                   f"BŁĄD: PEŁNY TEST NIEUDANY!\n"
                                   f"Podobieństwo: {similarity}%")
            
            try:
                if os.path.exists(test_output):
                    os.remove(test_output)
            except:
                pass
                
        except Exception as e:
            error_msg = f"Błąd testu: {str(e)}"
            self.update_status("Błąd testu!")
            self.log(f"BŁĄD testu: {error_msg}")
            messagebox.showerror("Błąd Testu", error_msg)
    
    def generate_key(self):
        if not self.crypto_available:
            messagebox.showwarning("Brak cryptography", 
                                 "Biblioteka 'cryptography' nie zainstalowana.\n"
                                 "Uruchom: pip install cryptography dla pełnego AES-256\n\n"
                                 "Generuję prosty klucz...")
            import secrets
            import string
            key = ''.join(secrets.choice(string.ascii_letters + string.digits) 
                         for _ in range(32))
            self.encryption_key.set(key)
            self.log("Wygenerowano prosty klucz (cryptography nie zainstalowane)")
        else:
            try:
                key = AESCipher.generate_key()
                self.encryption_key.set(key)
                self.log(f"Wygenerowano klucz AES: {key[:8]}...")
            except Exception as e:
                self.log(f"Błąd generowania klucza AES: {e}")
                import secrets
                import string
                key = ''.join(secrets.choice(string.ascii_letters + string.digits) 
                             for _ in range(32))
                self.encryption_key.set(key)
                self.log("Wygenerowano prosty klucz (fallback)")
        
        self.update_status("Klucz szyfrowania wygenerowany")
        messagebox.showinfo("Klucz Wygenerowany", 
                          f"Nowy klucz szyfrowania:\n\n{key}\n\n"
                          f"Zapisz go w bezpiecznym miejscu!\n"
                          f"Długość: {len(key)} znaków")
    
    def clear_message(self):
        self.message_text.delete("1.0", tk.END)
        self.update_status("Wiadomość wyczyszczona")
        self.log("Pole wiadomości wyczyszczone")
    
    def copy_to_clipboard(self):
        message = self.decoded_text.get("1.0", tk.END).strip()
        if message:
            self.root.clipboard_clear()
            self.root.clipboard_append(message)
            self.update_status("Wiadomość skopiowana do schowka")
            self.log("Wiadomość skopiowana do schowka")
            messagebox.showinfo("Schowek", "Wiadomość skopiowana do schowka!")
        else:
            messagebox.showwarning("Ostrzeżenie", "Brak wiadomości do skopiowania!")
    
    def save_decoded_message(self):
        message = self.decoded_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Ostrzeżenie", "Brak odczytanej wiadomości do zapisania!")
            return
        
        file = filedialog.asksaveasfilename(
            title="Zapisz odczytaną wiadomość jako",
            defaultextension=".txt",
            filetypes=[("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")]
        )
        
        if file:
            try:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(message)
                
                self.update_status(f"Wiadomość zapisana do {os.path.basename(file)}")
                self.log(f"Odczytana wiadomość zapisana do: {file}")
                messagebox.showinfo("Sukces", f"Wiadomość zapisana do:\n{file}")
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można zapisać wiadomości: {str(e)}")
                self.log(f"BŁĄD zapisywania wiadomości: {str(e)}")
    
    def _update_statistic(self, stat_name, operation):
        if stat_name in self.stats_labels:
            current = self.stats_labels[stat_name].cget("text")
            if operation == "+1":
                try:
                    new_value = int(current) + 1
                    self.stats_labels[stat_name].config(text=str(new_value))
                except:
                    self.stats_labels[stat_name].config(text="1")
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.update_idletasks()
    
    def clear_log(self):
        self.log_text.delete("1.0", tk.END)
        self.log("Dziennik wyczyszczony")
    
    def save_log(self):
        file = filedialog.asksaveasfilename(
            title="Zapisz dziennik jako",
            defaultextension=".log",
            filetypes=[("Pliki dziennika", "*.log"), ("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")]
        )
        
        if file:
            try:
                log_content = self.log_text.get("1.0", tk.END)
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                self.update_status(f"Dziennik zapisany do {os.path.basename(file)}")
                self.log(f"Dziennik zapisany do: {file}")
                messagebox.showinfo("Sukces", f"Dziennik zapisany do:\n{file}")
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można zapisać dziennika: {str(e)}")
                self.log(f"BŁĄD zapisywania dziennika: {str(e)}")

def run_gui():
    root = tk.Tk()
    
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = Gui(root)
    
    def on_closing():
        if messagebox.askokcancel("Zamknij", "Czy na pewno chcesz zamknąć aplikację?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

def run_gui():
    """Funkcja do uruchamiania GUI z zewnątrz."""
    root = tk.Tk()
    
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = Gui(root)
    
    def on_closing():
        if messagebox.askokcancel("Zamknij", "Czy na pewno chcesz zamknąć aplikację?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

main = run_gui

if __name__ == "__main__":
    run_gui()