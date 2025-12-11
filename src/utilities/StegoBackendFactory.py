from src.core.ImageStegoBackend import ImageStegoBackend
from src.utilities.ImageFormat import ImageFormat
from src.formats.png_backend import PngStegoBackend
from src.formats.bmp_backend import BmpStegoBackend
from src.formats.tiff_backend import TiffStegoBackend
from src.formats.jpeg_backend import JpegStegoBackend

class StegoBackendFactory:
    @staticmethod
    def create(fmt: ImageFormat) -> ImageStegoBackend:
        if fmt == ImageFormat.PNG:
            return PngStegoBackend()
        if fmt == ImageFormat.BMP:
            return BmpStegoBackend()
        if fmt == ImageFormat.TIFF:
            return TiffStegoBackend()
        if fmt == ImageFormat.JPEG:
            return JpegStegoBackend()
        raise ValueError(f"No backend for format: {fmt}")
