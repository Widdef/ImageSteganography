from imagesteganography.core.ImageStegoBackend import ImageStegoBackend
from imagesteganography.utilities.ImageFormat import ImageFormat
from imagesteganography.formats.png_backend import PngStegoBackend
from imagesteganography.formats.bmp_backend import BmpStegoBackend
from imagesteganography.formats.tiff_backend import TiffStegoBackend
from imagesteganography.formats.jpeg_backend import JpegStegoBackend

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
