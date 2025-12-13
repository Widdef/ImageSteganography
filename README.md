# ImageSteganography

<p>ImageSteganography to narzędzie do ukrywania i odczytywania tajnych wiadomości w plikach obrazów przy użyciu technik steganografii. Steganografia to technika ukrywania informacji w innej informacji tak, by obecność ukrytych danych nie była oczywista — w przypadku obrazów polega to na modyfikowaniu bitów pikseli w sposób praktycznie niedostrzegalny dla ludzkiego oka.</p>

## Wymagania
Wymagania środowiska, żeby skompilować pakiety dla wirtualnego środowiska python:
* Python 3.14+
* kompilator C i C++, np. gcc
* python3-devel
* python3-tkinter 
* tk-devel
## Instalacja
### Sklonuj repozytorium
```console
    git clone https://github.com/Widdef/ImageSteganography.git<br>
    cd ImageSteganography
```
### Następnie wykonaj 
```console
    python bootstrap.py 
```
<p>Skrypt bootstrap stworzy wirtualne środowisko venv z zaistalowanymi i skompilowanymi bibliotekami wymaganymi do działania programu. program należy uruchamiać wewnątrz tego środowiska.</p>
<p></p>Wejście do środowiska witrualnego:</p>

### Linux
```console
    source ./venv/bin/activate 
```
### Windows 
```console
    ./venv/Source/Activate.ps1
```
## Instrukcja korzystania:

### CLI
<p>Część funkcjonalności jest możliwe do wykorzystania z poziomu CLI i działa bezpośrednio z linii komend w środowisku wirtualnym:</p>
<p>Szyfrowanie:</p>

```console
    stego encode [image_path] [message] [output_path]
```
<p>Deszyfrowanie:</p>

```console
    stego decode [image_path]
```

### GUI
<p>Aplikacje posiada GUI, które uruchamiamy za pomocą:</p>

```console
   python main.py
```
