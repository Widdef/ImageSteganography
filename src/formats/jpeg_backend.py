from src.core.ImageStegoBackend import ImageStegoBackend

class JpegStegoBackend(ImageStegoBackend):
    def encode(self, input_path: str, message: str, output_path: str) -> str:
        # TODO: Implementacja stego dla JPEG 
        raise NotImplementedError("JPEG steganography not implemented yet.")

    def decode(self, input_path: str) -> str:
        # TODO
        raise NotImplementedError("JPEG steganography not implemented yet.")
