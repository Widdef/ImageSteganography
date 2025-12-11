from PIL import Image
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL.Image import PixelAccess # type: ignore

class LsbMixin:
    """
    Mieszanka z implementacją prostego LSB dla obrazów RGB/RGBA.
    Zakładamy, że zapis/odczyt idzie tylko w kanałach RGB.
    """

    HEADER_BITS = 32  # np. 32 bity na długość wiadomości w bajtach

    def _image_to_pixels(self, img: Image.Image) -> tuple[Image.Image, PixelAccess]:
        # wymuś kopię aby load() zawsze działało 
        img = img.copy()
        
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        
        pixels = img.load()
        if pixels is None:
            raise RuntimeError("Image.load() returned None — cannot access pixels")
        
        return img, pixels
    

    def _get_rgba(self, pixels: PixelAccess, x: int, y: int) -> tuple[int, int, int, int]:
        """Zwraca zawsze (r, g, b, a) niezależnie od trybu obrazu."""
        # Zapewnia zgodność typów pod Pylance
        value = pixels[x, y]

        if isinstance(value, tuple):
            if len(value) == 4:
                return value  # RGBA
            if len(value) == 3:
                r, g, b = value
                return r, g, b, 255  # RGB -> RGBA
            v = int(value[0])
            return v, v, v, 255
        else:
            # grayscale / float / int
            v = int(value)
            return v, v, v, 255    

    def _capacity_in_bits(self, img: Image.Image) -> int:
        w, h = img.size
        channels_per_pixel = 3  # użyjemy RGB
        return w * h * channels_per_pixel

    def _message_to_bits(self, message: str) -> str:
        data = message.encode("utf-8")
        length = len(data)
        # nagłówek: 32 bity długości
        header = length.to_bytes(4, byteorder="big")
        full = header + data
        return "".join(f"{byte:08b}" for byte in full)

    def _bits_to_message(self, bits: str) -> str:
        # najpierw 32 bity = 4 bajty długości
        header_bits = bits[: self.HEADER_BITS]
        length = int(header_bits, 2)
        msg_bits = bits[self.HEADER_BITS : self.HEADER_BITS + length * 8]
        data = int(msg_bits, 2).to_bytes(length, byteorder="big")
        return data.decode("utf-8")

    def _encode_lsb(self, input_path: str, message: str, output_path: str, fmt: str) -> str:
        img = Image.open(input_path)
        img, pixels = self._image_to_pixels(img)

        bits = self._message_to_bits(message)
        if len(bits) > self._capacity_in_bits(img):
            raise ValueError("Wiadomość jest za długa dla tego obrazu.")

        w, h = img.size
        bit_index = 0
        for y in range(h):
            for x in range(w):
                if bit_index >= len(bits):
                    break
                r, g, b, a = self._get_rgba(pixels, x, y)
                channels = [r, g, b]
                for i in range(3):
                    if bit_index >= len(bits):
                        break
                    channel = channels[i]
                    channel &= 0b11111110  # zerujemy najmłodszy bit
                    channel |= int(bits[bit_index])
                    channels[i] = channel
                    bit_index += 1

                pixels[x, y] = (*channels, a)

            if bit_index >= len(bits):
                break

        img.save(output_path, format=fmt)
        return output_path

    def _decode_lsb(self, input_path: str) -> str:
        img = Image.open(input_path)
        img, pixels = self._image_to_pixels(img)

        w, h = img.size
        bit_stream = []

        # Najpierw czytamy nagłówek, żeby wiedzieć ile dalej
        bits_needed_for_header = self.HEADER_BITS
        header_bits = []
        x = y = 0

        # 1. Odczyt nagłówka:
        for y in range(h):
            for x in range(w):
                r, g, b, *rest = pixels[x, y]
                for channel in (r, g, b):
                    header_bits.append(str(channel & 1))
                    if len(header_bits) >= bits_needed_for_header:
                        break
                if len(header_bits) >= bits_needed_for_header:
                    break
            if len(header_bits) >= bits_needed_for_header:
                break

        length = int("".join(header_bits), 2)
        msg_bits_needed = length * 8
        msg_bits = []

        # 2. Odczyt reszty wiadomości, kontynuując od kolejnego kanału
        # Uproszczenie: przechodzimy po obrazie od początku jeszcze raz
        # (wydajnościowo to OK dla projektu zaliczeniowego).
        idx = 0
        for y in range(h):
            for x in range(w):
                r, g, b, *rest = pixels[x, y]
                for channel in (r, g, b):
                    if idx < bits_needed_for_header:
                        idx += 1
                        continue
                    msg_bits.append(str(channel & 1))
                    if len(msg_bits) >= msg_bits_needed:
                        break
                if len(msg_bits) >= msg_bits_needed:
                    break
            if len(msg_bits) >= msg_bits_needed:
                break

        all_bits = "".join(header_bits + msg_bits)
        return self._bits_to_message(all_bits)
