from imagesteganography.core.ImageStegoBackend import ImageStegoBackend
from imagesteganography.core.LsbMixin import LsbMixin

class BmpStegoBackend(ImageStegoBackend, LsbMixin):
    def __init__(self, anti_forensic_noise: bool, noise_ratio: float):
        self.anti_forensic_noise = anti_forensic_noise
        self.noise_ratio = noise_ratio

    def encode(self, input_path: str, message: str, output_path: str) -> str:
        return self._encode_lsb(input_path, message, output_path, 
                                fmt="BMP", 
                                anti_forensic_noise = self.anti_forensic_noise,
                                noise_ratio = self.noise_ratio)

    def decode(self, input_path: str) -> str:
        return self._decode_lsb(input_path)
