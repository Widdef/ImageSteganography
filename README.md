# ImageSteganography

ImageSteganography to narzędzie do ukrywania i odczytywania tajnych wiadomości w plikach obrazów przy użyciu technik steganografii. Steganografia to technika ukrywania informacji w innej informacji tak, by obecność ukrytych danych nie była oczywista — w przypadku obrazów polega to na modyfikowaniu bitów pikseli w sposób praktycznie niedostrzegalny dla ludzkiego oka.

## Wymagania

Wymagania środowiska, żeby skompilować pakiety dla wirtualnego środowiska Python:

- Python 3.14+
- Kompilator C i C++, np. gcc
- python3-devel
- python3-tkinter
- tk-devel

## Instalacja

### Sklonuj repozytorium

```bash
git clone https://github.com/Widdef/ImageSteganography.git
cd ImageSteganography
```

### Następnie wykonaj

```bash
python bootstrap.py
```

Skrypt `bootstrap` stworzy wirtualne środowisko `venv` z zainstalowanymi i skompilowanymi bibliotekami wymaganymi do działania programu. Program należy uruchamiać wewnątrz tego środowiska.

### Wejście do środowiska wirtualnego

**Linux:**

```bash
source ./venv/bin/activate
```

**Windows:**

```powershell
./venv/Scripts/Activate.ps1
```

## Instrukcja korzystania

### CLI

Część funkcjonalności jest możliwa do wykorzystania z poziomu CLI i działa bezpośrednio z linii komend w środowisku wirtualnym:

**Szyfrowanie:**

```bash
stego encode [image_path] [message] [output_path]
```

**Deszyfrowanie:**

```bash
stego decode [image_path]
```

### GUI

Aplikacja posiada GUI, które uruchamiamy za pomocą:

```bash
python main.py
```

### Graficzny interfejs użytkownika (GUI)

Po uruchomieniu `python main.py` otworzy się zaawansowany interfejs graficzny z następującymi funkcjami:

#### Panel główny
- 📁 **Wczytaj Obraz** – wybierz obraz do przetworzenia (obsługiwane formaty: PNG, BMP, JPEG, TIFF)
- 💾 **Zapisz Obraz** – zapisz przetworzony obraz
- Podgląd obrazu – wyświetla aktualnie załadowany obraz

#### Zakładka "🔒 Koduj"
- Pole wiadomości – wpisz wiadomość do ukrycia w obrazie
- **Szyfrowanie AES-256**:
  - Pole na klucz szyfrowania (możliwość pokazania/ukrycia)
  - Przycisk "🎲 Generuj Klucz" – generuje losowy klucz
  - Status szyfrowania – informuje o dostępności modułu cryptography
- **Opcje Zaawansowane**:
  - Suwak szumu anti-forensic (0-100%) – reguluje poziom szumu dodawanego do wolnych bitów
    - 0% = brak szumu
    - 1-100% = dodaje szum do nieużywanych bitów (zalecane 5-15%)
  - Weryfikuj po zakodowaniu – automatycznie sprawdza czy zakodowana wiadomość zgadza się z oryginałem
- 📥 **Koduj Wiadomość** – rozpoczyna proces ukrywania wiadomości

#### Zakładka "🔓 Dekoduj"
- 📂 **Wczytaj Zakodowany Obraz** – wybierz obraz z ukrytą wiadomością
- **Deszyfrowanie AES**:
  - Pole na klucz deszyfrowania (jeśli wiadomość była szyfrowana)
  - Możliwość pokazania/ukrycia klucza
- 🔍 **Dekoduj Wiadomość** – odczytuje ukrytą wiadomość
- Odczytywana Wiadomość – wyświetla odczytany tekst
- 📋 **Kopiuj** – kopiuje wiadomość do schowka
- 💾 **Zapisz** – zapisuje wiadomość do pliku tekstowego

#### Zakładka "📊 Analizuj"
- **Pojemność Obrazu**:
  - Oblicza maksymalny rozmiar wiadomości jaką można ukryć
  - Przycisk "🔢 Oblicz Pojemność"
- **Jakość Obrazu (PSNR)**:
  - Oblicza stosunek sygnału do szumu między oryginałem a zakodowanym obrazem
  - Wartości: >40dB (doskonała), 30-40dB (dobra), 20-30dB (średnia), <20dB (słaba)
  - Przycisk "📊 Oblicz PSNR"
- **Weryfikacja Wiadomości**:
  - Sprawdza integralność zakodowanego obrazu
  - Przycisk "✓ Zweryfikuj Integralność"
- **Testy Automatyczne**:
  - Uruchamia pełny test: kodowanie → dekodowanie → porównanie
  - Przycisk "🧪 Uruchom Pełny Test"

#### Panel informacyjny
- Lista dostępnych funkcji projektu
- Statusy modułów (szyfrowanie, JPEG)
- Instrukcje korzystania z szumu i szyfrowania
- Statystyki użycia programu

#### Dziennik aktywności
- Loguje wszystkie operacje z timestampem
- Możliwość czyszczenia i zapisywania dziennika do pliku

#### Pasek statusu
- Wyświetla aktualny status operacji
- Informuje o stanie silnika (dostępność modułów)

## 🔒 Funkcje bezpieczeństwa

### Szyfrowanie AES-256
- Opcjonalne szyfrowanie wiadomości przed ukryciem w obrazie
- Wymaga klucza do odczytu
- Generowanie bezpiecznych kluczy
- Kompatybilność z modułem cryptography

### Szum anti-forensic
- Automatyczne dodawanie szumu do nieużywanych bitów
- Utrudnia wykrycie steganografii przez analizę statystyczną
- Regulowany poziom (0-100%)
- Domyślnie włączony z optymalnym poziomem 5%

## 📁 Obsługiwane formaty

| Format | Metoda steganografii                | Uwagi                               |
|--------|-------------------------------------|-------------------------------------|
| BMP    | LSB (Least Significant Bit)         | Bez strat, wysoka pojemność         |
| PNG    | LSB                                 | Bezstratna kompresja                |
| TIFF   | LSB                                 | Wysoka jakość, duże pliki           |
| JPEG   | DCT (Discrete Cosine Transform)     | Stratna kompresja, wymaga jpegio    |

## 🧪 Testowanie

Program zawiera zintegrowany system testów:

- Testy jednostkowe – weryfikacja poszczególnych funkcji
- Testy integracyjne – pełny cykl kodowania/dekodowania
- Automatyczna weryfikacja – sprawdzenie zgodności wiadomości

Uruchom testy:

```bash
python -m pytest tests/
```

## 💡 Porady i wskazówki

- Rozmiar wiadomości – nie przekraczaj pojemności obrazu (użyj "Oblicz Pojemność")
- Szum anti-forensic – użyj 5-15% dla optymalnej równowagi między ukrywalnością a jakością
- Formaty bezstratne (BMP, PNG, TIFF) – lepsze dla ważnych danych
- JPEG – użyj tylko gdy rozmiar pliku ma znaczenie (straty jakości)
- Klucze szyfrowania – zawsze zapisuj w bezpiecznym miejscu
- Weryfikacja – zawsze weryfikuj po kodowaniu dla ważnych wiadomości

## 📊 Przykłady użycia

### Przykład 1: Proste ukrywanie wiadomości
1. Uruchom `python main.py`
2. Wczytaj obraz BMP/PNG
3. Wpisz wiadomość w polu tekstowym
4. Ustaw poziom szumu (np. 10%)
5. Kliknij "📥 Koduj Wiadomość"
6. Zapisz zakodowany obraz

### Przykład 2: Bezpieczne ukrywanie z szyfrowaniem
1. Wczytaj obraz
2. Wpisz tajną wiadomość
3. Kliknij "🎲 Generuj Klucz" i zapisz go
4. Wprowadź klucz w polu szyfrowania
5. Zakoduj obraz
6. Do odczytu potrzebny będzie ten sam klucz

### Przykład 3: Analiza jakości
1. Zakoduj wiadomość w obrazie
2. Przejdź do zakładki "📊 Analizuj"
3. Kliknij "📊 Oblicz PSNR"
4. Porównaj oryginalny i zakodowany obraz
5. Sprawdź czy zmiany są niedostrzegalne (PSNR > 40dB)
