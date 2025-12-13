from imagesteganography.core.ImageStegoBackend import ImageStegoBackend
from imagesteganography.utilities.ImageFormat import ImageFormat
from imagesteganography.formats.png_backend import PngStegoBackend
from imagesteganography.formats.bmp_backend import BmpStegoBackend
from imagesteganography.formats.tiff_backend import TiffStegoBackend
from imagesteganography.formats.jpeg_backend import JpegStegoBackend

class StegoBackendFactory:
    @staticmethod
    def create(fmt: ImageFormat, anti_forensic_noise: bool = False, noise_ratio: float = 0.05) -> ImageStegoBackend:
        if fmt == ImageFormat.PNG:
            return PngStegoBackend(anti_forensic_noise = anti_forensic_noise, noise_ratio = noise_ratio)
        if fmt == ImageFormat.BMP:
            return BmpStegoBackend(anti_forensic_noise = anti_forensic_noise, noise_ratio = noise_ratio)
        if fmt == ImageFormat.TIFF:
            return TiffStegoBackend(anti_forensic_noise = anti_forensic_noise, noise_ratio = noise_ratio)
        if fmt == ImageFormat.JPEG:
            return JpegStegoBackend(anti_forensic_noise = anti_forensic_noise, noise_ratio = noise_ratio)
        raise ValueError(f"No backend for format: {fmt}")
