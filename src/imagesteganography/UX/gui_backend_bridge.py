import os
from typing import Optional, Tuple, Dict, Any
from PIL import Image
import numpy as np
import hashlib

from imagesteganography.core.StegoService import StegoService
from imagesteganography.utilities.ImageFormat import ImageFormat

class GUIBackendBridge:
    def __init__(self):
        self.stego_service = StegoService()
        self.stats = {
            "images_processed": 0,
            "messages_encoded": 0,
            "messages_decoded": 0,
            "successful_tests": 0
        }
    
    def encode_message(self, image_path: str, message: str, output_path: Optional[str] = None) -> Tuple[bool, str, str]:
        try:
            if not os.path.exists(image_path):
                return False, "", f"Obraz nie istnieje: {image_path}"
            
            image_format = ImageFormat.from_path(image_path)
            message_hash = hashlib.sha256(message.encode()).hexdigest()
            
            result_path = self.stego_service.hide_message(
                image_path=image_path,
                message=message,
                image_format=image_format,
                output_path=output_path
            )
            
            self.stats["images_processed"] += 1
            self.stats["messages_encoded"] += 1
            
            return True, result_path, f"Wiadomość zakodowana pomyślnie!\nZapisano do: {os.path.basename(result_path)}"
            
        except ValueError as e:
            return False, "", f"Wiadomość za długa dla tego obrazu\n{e}"
        except Exception as e:
            return False, "", f"Kodowanie nie powiodło się: {str(e)}"
    
    def decode_message(self, image_path: str) -> Tuple[bool, str, str]:
        try:
            if not os.path.exists(image_path):
                return False, "", f"Obraz nie istnieje: {image_path}"
            
            image_format = ImageFormat.from_path(image_path)
            message = self.stego_service.reveal_message(
                image_path=image_path,
                image_format=image_format
            )
            
            self.stats["images_processed"] += 1
            self.stats["messages_decoded"] += 1
            
            return True, message, "Wiadomość odczytana pomyślnie!"
            
        except Exception as e:
            return False, "", f"Odczytywanie nie powiodło się: {str(e)}"
    
    def verify_message(self, original: str, decoded: str) -> Tuple[bool, str, float]:
        try:
            from tests.verification import verify_message, calculate_similarity
        except ImportError:
            from verification import verify_message, calculate_similarity
        
        is_match, msg = verify_message(original, decoded)
        similarity = calculate_similarity(original, decoded)
        
        if is_match:
            self.stats["successful_tests"] += 1
            
        return is_match, msg, similarity
    
    def calculate_capacity(self, image_path: str) -> Tuple[bool, int, str]:
        try:
            if not os.path.exists(image_path):
                return False, 0, f"Obraz nie istnieje: {image_path}"
            
            img = Image.open(image_path)
            width, height = img.size
            
            capacity_bits = width * height * 3
            capacity_bytes = capacity_bits // 8
            capacity_bytes -= 4
            
            if capacity_bytes < 0:
                capacity_bytes = 0
            
            return True, capacity_bytes, f"Pojemność obliczona dla obrazu {width}x{height}"
            
        except Exception as e:
            return False, 0, f"Obliczanie pojemności nie powiodło się: {str(e)}"
    
    def calculate_psnr(self, original_path: str, encoded_path: str) -> Tuple[bool, float, str]:
        try:
            if not os.path.exists(original_path):
                return False, 0.0, f"Oryginalny obraz nie istnieje: {original_path}"
            if not os.path.exists(encoded_path):
                return False, 0.0, f"Zakodowany obraz nie istnieje: {encoded_path}"
            
            img1 = np.array(Image.open(original_path).convert('RGB'))
            img2 = np.array(Image.open(encoded_path).convert('RGB'))
            
            mse = np.mean((img1 - img2) ** 2)
            
            if mse == 0:
                psnr = 100.0
            else:
                max_pixel = 255.0
                psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
            
            quality = "Doskonała" if psnr > 40 else "Dobra" if psnr > 30 else "Akceptowalna" if psnr > 20 else "Słaba"
            
            return True, psnr, f"PSNR obliczone: {quality} jakość"
            
        except Exception as e:
            return False, 0.0, f"Obliczanie PSNR nie powiodło się: {str(e)}"
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        try:
            if not os.path.exists(image_path):
                return {"error": f"Obraz nie istnieje: {image_path}"}
            
            img = Image.open(image_path)
            
            return {
                "filename": os.path.basename(image_path),
                "size": img.size,
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_stats(self) -> Dict[str, int]:
        return self.stats.copy()