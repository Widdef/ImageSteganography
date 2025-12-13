import base64
import hashlib
import os
from typing import Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


class AESCipher:
    """
    Klasa do szyfrowania i deszyfrowania wiadomości AES-256-CBC.
    """
    
    @staticmethod
    def _derive_key(password: str, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """
        Pochodzi klucz 256-bit i IV z hasła używając PBKDF2.
        
        Args:
            password: Hasło jako string
            salt: Opcjonalna sól (jeśli None, generuje nową)
            
        Returns:
            tuple: (klucz, iv, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        #Uzyj PBKDF2 z 100000 iteracji
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000,
            dklen=32  # 256-bit klucz
        )
        
        # Generuj IV z hasła i soli
        iv = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt + b'iv',
            10000,
            dklen=16  # 128-bit IV
        )
        
        return key, iv, salt
    
    @staticmethod
    def encrypt(message: str, password: str) -> bytes:
        """
        Szyfruje wiadomość używając AES-256-CBC.
        
        Args:
            message: Wiadomość do zaszyfrowania
            password: Hasło do szyfrowania
            
        Returns:
            bytes: Zaszyfrowane dane w formacie: salt + ciphertext
        """
        if not password:
            return message.encode('utf-8')
        
        plaintext = message.encode('utf-8')
        
        key, iv, salt = AESCipher._derive_key(password)
        
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return salt + ciphertext
    
    @staticmethod
    def decrypt(encrypted_data: bytes, password: str) -> str:
        """
        Deszyfruje wiadomość zaszyfrowaną AES-256-CBC.
        
        Args:
            encrypted_data: Zaszyfrowane dane (salt + ciphertext)
            password: Hasło użyte do szyfrowania
            
        Returns:
            str: Odszyfrowana wiadomość
            
        Raises:
            ValueError: Jeśli deszyfrowanie się nie powiedzie
        """
        if not password:
            try:
                return encrypted_data.decode('utf-8')
            except:
                raise ValueError("Nieprawidłowe dane do deszyfrowania")
        
        if len(encrypted_data) < 32:  # min 16 bajtów soli + 16 bajtów danych
            raise ValueError("Zbyt krótkie zaszyfrowane dane")
        
        salt = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        key, iv, _ = AESCipher._derive_key(password, salt)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext.decode('utf-8')
    
    @staticmethod
    def generate_key() -> str:
        """
        Generuje losowy klucz AES w formacie Base64.
        
        Returns:
            str: 32-bajtowy klucz zakodowany w Base64
        """
        key = os.urandom(32)
        return base64.urlsafe_b64encode(key).decode('utf-8')[:32]


class SimpleAESCipher:
    """
    Uproszczona wersja AES dla kompatybilności (bez zewnętrznych bibliotek).
    Używa tylko standardowej biblioteki Pythona.
    """
    
    @staticmethod
    def encrypt_simple(message: str, password: str) -> bytes:
        """
        Proste szyfrowanie XOR-based (tylko dla demonstracji).
        NIE UŻYWAJ W PRODUKCJI!
        """
        if not password:
            return message.encode('utf-8')
        
        key = hashlib.sha256(password.encode('utf-8')).digest()
        message_bytes = message.encode('utf-8')
        
        encrypted = bytearray()
        for i, byte in enumerate(message_bytes):
            key_byte = key[i % len(key)]
            encrypted.append(byte ^ key_byte)
        
        return b"SIMPLE_AES:" + bytes(encrypted)
    
    @staticmethod
    def decrypt_simple(encrypted: bytes, password: str) -> str:
        """
        Proste deszyfrowanie XOR-based.
        """
        if not password:
            return encrypted.decode('utf-8')
        
        if encrypted.startswith(b"SIMPLE_AES:"):
            encrypted = encrypted[11:]
        
        key = hashlib.sha256(password.encode('utf-8')).digest()
        
        decrypted = bytearray()
        for i, byte in enumerate(encrypted):
            key_byte = key[i % len(key)]
            decrypted.append(byte ^ key_byte)
        
        return decrypted.decode('utf-8')