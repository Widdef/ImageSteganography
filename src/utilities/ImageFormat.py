from enum import Enum

class ImageFormat(Enum):
    PNG = "png"
    BMP = "bmp"
    TIFF = "tiff"
    JPEG = "jpeg"

    @staticmethod
    def from_path(path: str) -> "ImageFormat":
        ext = path.split(".")[-1].lower()
        for f in ImageFormat:
            if f.value == ext:
                return f
        raise ValueError(f"Unsupported image extension: {ext}")