import os
from typing import Optional
from src.utilities.ImageFormat import ImageFormat
from src.utilities.StegoBackendFactory import StegoBackendFactory


class StegoService:
    """
    Warstwa pośrednia między GUI a konkretnymi backendami.
    GUI używa tylko tej klasy.
    """

    def __init__(self, backend_factory: StegoBackendFactory | None = None):
        self.backend_factory = backend_factory or StegoBackendFactory()

    def _default_output_path(self, input_path: str) -> str:
        base, ext = os.path.splitext(input_path)
        return f"{base}_stego{ext}"

    def hide_message(
        self,
        image_path: str,
        message: str,
        image_format: ImageFormat,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Ukrywa wiadomość i zwraca ścieżkę do nowego pliku.
        """
        backend = self.backend_factory.create(image_format)
        if output_path is None:
            output_path = self._default_output_path(image_path)
        return backend.encode(image_path, message, output_path)

    def reveal_message(self, image_path: str, image_format: ImageFormat) -> str:
        """
        Odczytuje wiadomość i zwraca ją jako tekst.
        """
        backend = self.backend_factory.create(image_format)
        return backend.decode(image_path)
