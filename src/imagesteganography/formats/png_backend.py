from imagesteganography.core.ImageStegoBackend import ImageStegoBackend
from imagesteganography.core.LsbMixin import LsbMixin


class PngStegoBackend(ImageStegoBackend, LsbMixin):
    def encode(self, input_path: str, message: str, output_path: str) -> str:
        return self._encode_lsb(input_path, message, output_path, fmt="PNG")

    def decode(self, input_path: str) -> str:
        return self._decode_lsb(input_path)
