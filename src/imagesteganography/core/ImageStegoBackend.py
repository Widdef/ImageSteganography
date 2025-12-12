from abc import ABC, abstractmethod

class ImageStegoBackend(ABC):
    """Interfejs dla konkretnych implementacji steganografii obrazowej."""

    @abstractmethod
    def encode(self, input_path: str, message: str, output_path: str) -> str:
        """
        Ukryj 'message' w obrazie 'input_path' i zapisz w 'output_path'.
        Zwraca ścieżkę do nowego pliku.
        """
        raise NotImplementedError

    @abstractmethod
    def decode(self, input_path: str) -> str:
        """
        Odczytaj ukrytą wiadomość z obrazu 'input_path'.
        Zwraca odczytany tekst.
        """
        raise NotImplementedError
