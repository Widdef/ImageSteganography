import os
import typer
from imagesteganography.core.StegoService import StegoService
from imagesteganography.utilities.ImageFormat import ImageFormat

app = typer.Typer(help="Image steganography (LSB) CLI")

service = StegoService()

@app.command()
def encode(image: str, message: str, output: str = None):
    """
    Ukrywa wiadomość w obrazie i zapisuje wynik w pliku wyjściowym.
    """
    fmt_enum = ImageFormat.from_path(image)
    result = service.hide_message(image, message, fmt_enum, output)
    typer.echo(f"Zapisano: {result}")


@app.command()
def decode(image: str):
    """
    Odczytuje wiadomość ukrytą w obrazie IMAGE.
    """
    fmt_enum = ImageFormat.from_path(image)
    msg = service.reveal_message(image, fmt_enum)
    typer.echo(msg)

def main() -> None:
    """
    Punkt wejścia dla konsolowej komendy `stego`.
    """
    app()

if __name__ == "__main__":
    main()