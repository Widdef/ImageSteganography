from __future__ import annotations

import struct
import jpegio as jio   

from typing import List

from imagesteganography.core.ImageStegoBackend import ImageStegoBackend
from imagesteganography.utilities.config import get_config

config = get_config()

class JpegStegoBackend(ImageStegoBackend):
    """
    Prosta steganografia dla JPEG DCT:
    - pracujemy bezpośrednio na współczynnikach DCT,
    - w LSB współczynników kodujemy:
        [32 bity długości wiadomości w bajtach][dane UTF-8].

    Prosty LSB w DCT, nie działa po pixelach.
    """

    HEADER_BITS = int(config.get("PARAMS","HEADER_BITS")) #type: ignore

    def __init__(self, anti_forensic_noise: bool, noise_ratio: float):
        self.anti_forensic_noise = anti_forensic_noise
        self.noise_ratio = noise_ratio

    def encode(self, input_path: str, message: str, output_path: str) -> str:
        """
        Zapisuje 'message' w pliku JPEG 'input_path' i zapisuje do 'output_path'.
        Zwraca ścieżkę output_path.
        """
        # 1. przygotuj payload (nagłówek + dane)
        data = message.encode("utf-8")
        length = len(data)
        header = struct.pack(">I", length)  # 4 bajty big-endian
        full = header + data
        bits = self._bytes_to_bits(full)

        # 2. wczytaj JPEG, zbierz pozycje współczynników
        jpeg = jio.read(input_path)
        positions = self._collect_positions(jpeg)

        capacity = len(positions)
        if len(bits) > capacity:
            raise ValueError(
                f"Wiadomość jest za długa dla tego JPEG-a: "
                f"potrzebne {len(bits)} bitów, dostępne {capacity}."
            )

        # 3. osadzanie bitów w LSB współczynników DCT
        for bit_idx, bit in enumerate(bits):
            comp_idx, i, j = positions[bit_idx]
            coeff_arr = jpeg.coef_arrays[comp_idx]
            coeff = int(coeff_arr[i, j])

            # ustaw LSB na wartość bitu
            if bit == 0:
                coeff &= ~1
            else:
                coeff |= 1

            coeff_arr[i, j] = coeff
        # 4. opcjonalny szum anti-forensic
        if self.anti_forensic_noise:
            self._apply_anti_forensic_noise(jpeg, positions, used_bits=len(bits))

        # 5. zapis nowego JPEG
        jio.write(jpeg, output_path)
        return output_path

    def decode(self, input_path: str) -> str:
        """
        Odczytuje wiadomość z JPEG-a.
        Zakładamy, że obraz był zakodowany powyższą metodą.
        """
        jpeg = jio.read(input_path)
        positions = self._collect_positions(jpeg)

        if len(positions) < self.HEADER_BITS:
            raise ValueError("Obraz nie zawiera nawet pełnego nagłówka.")

        # 1. odczytaj 32 bity nagłówka (długość w bajtach)
        header_bits: List[int] = []
        for idx in range(self.HEADER_BITS):
            comp_idx, i, j = positions[idx]
            coeff = int(jpeg.coef_arrays[comp_idx][i, j])
            header_bits.append(coeff & 1)

        header_bytes = self._bits_to_bytes(header_bits)
        (msg_len,) = struct.unpack(">I", header_bytes)

        # 2. odczytaj msg_len bajtów (msg_len * 8 bitów)
        data_bits_len = msg_len * 8
        total_bits_needed = self.HEADER_BITS + data_bits_len

        if total_bits_needed > len(positions):
            raise ValueError(
                "Deklarowana długość wiadomości przekracza pojemność osadzonych bitów."
            )

        data_bits: List[int] = []
        for idx in range(self.HEADER_BITS, total_bits_needed):
            comp_idx, i, j = positions[idx]
            coeff = int(jpeg.coef_arrays[comp_idx][i, j])
            data_bits.append(coeff & 1)

        data_bytes = self._bits_to_bytes(data_bits)
        try:
            return data_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("Nie udało się zdekodować wiadomości jako UTF-8.")

    def _bytes_to_bits(self, data: bytes) -> list[int]:
        """Zamiana bajtów na listę bitów (0/1), MSB first."""
        bits: list[int] = []
        for b in data:
            for i in range(7, -1, -1):
                bits.append((b >> i) & 1)
        return bits

    def _bits_to_bytes(self, bits: list[int]) -> bytes:
        """Zamiana listy bitów (0/1) na bajty."""
        if len(bits) % 8 != 0:
            raise ValueError("Długość strumienia bitów nie jest podzielna przez 8.")
        out = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for bit in bits[i:i+8]:
                byte = (byte << 1) | (bit & 1)
            out.append(byte)
        return bytes(out)

    def _collect_positions(self, jpeg) -> list[tuple[int, int, int]]:
        """
        Zwraca listę pozycji współczynników DCT:
        [(comp_idx, i, j), ...]

        Dla uproszczenia:
        - używamy wszystkich niezerowych współczynników,
        - wszystkich komponentów (Y, Cb, Cr),
        - nie rozróżniamy DC/AC
        """
        positions: list[tuple[int, int, int]] = []

        for comp_idx, arr in enumerate(jpeg.coef_arrays):
            # arr jest np. typu np.ndarray[int16]
            h, w = arr.shape
            for i in range(h):
                for j in range(w):
                    positions.append((comp_idx, i, j))

        return positions

    def _apply_anti_forensic_noise(
            self,
            jpeg,
            positions: list[tuple[int, int, int]],
            used_bits: int,
        ) -> None:
            """
            Dodaje lekki szum do nieużywanych współczynników DCT,
            nie ruszając tych, które zmodyfikowaliśmy
            """
            import random

            free_positions = positions[used_bits:]
            if not free_positions:
                return

            n_to_modify = int(len(free_positions) * self.noise_ratio)
            if n_to_modify <= 0:
                return

            for comp_idx, i, j in random.sample(free_positions, n_to_modify):
                coeff_arr = jpeg.coef_arrays[comp_idx]
                coeff = int(coeff_arr[i, j])

                # Minimalna zmiana: losowy LSB
                bit = 1 if random.random() < 0.5 else 0
                coeff = (coeff & ~1) | bit

                coeff_arr[i, j] = coeff