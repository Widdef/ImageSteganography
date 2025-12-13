from enum import Enum
import os

class ImageFormat(Enum):
    PNG = "png"
    BMP = "bmp"
    TIFF = "tiff"
    JPEG = "jpeg"

    @classmethod
    def from_path(cls, path: str) -> "ImageFormat":
        _, ext = os.path.splitext(path)
        if not ext:
            raise ValueError("File has no extension")

        ext = ext[1:].lower()  # bez kropki
        for fmt in cls:
            if fmt.value == ext:
                return fmt

        raise ValueError(f"Unsupported image format: {ext}")