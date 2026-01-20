# Jak wysłać kod na GitHub (Krok po kroku)

Masz dwie drogi: najprostszą (przez przeglądarkę) oraz profesjonalną (przez komendy Git).

## Metoda 1: Przez przeglądarkę (Najprostsza)
Jeśli nie masz zainstalowanego Gita na komputerze, zrób to tak:
1. Wejdź na swoje repozytorium na GitHub.
2. Kliknij przycisk **Add file** -> **Upload files**.
3. Przeciągnij z folderu `003 - Watermark` tylko te pliki:
   - Wszystkie pliki `.py` (`gui.py`, `engine.py` itd.)
   - Wszystkie nowe pliki, które stworzyłem (`README.md`, `.gitignore`, `requirements.txt`)
   - `icon.ico`, `logo.png`
   - `PhotoBrand.spec`, `version_info.txt`
4. **Pamiętaj:** Nie wrzucaj folderów `dist`, `build`, `__pycache__` ani `fonts`.
5. Kliknij **Commit changes** na dole.

## Metoda 2: Przez komendy (Jeśli masz zainstalowanego Gita)
Otwórz terminal w folderze projektu i wpisz kolejno:

1. Inicjalizacja (jeśli to nowe repo):
   ```powershell
   git init
   ```
2. Dodanie adresu (jeśli jeszcze nie dodany):
   ```powershell
   git remote add origin https://github.com/NSPCserwis/PhotoBrand.git
   ```
3. Przygotowanie plików (dzięki `.gitignore` Git sam pominie ciężkie foldery!):
   ```powershell
   git add .
   ```
4. Podpisanie zmian:
   ```powershell
   git commit -m "Initial commit - Photo Brand V1.1"
   ```
5. wysłanie:
   ```powershell
   git push -u origin main
   ```

---

### 💡 Ważna wskazówka:
Dzięki temu, że stworzyłem plik `.gitignore`, jeśli użyjesz **Metody 2**, możesz bezpiecznie wpisać `git add .` – Git sam "wyfiltruje" śmieci i wyśle tylko czysty kod.

Daj znać, na którym etapie jesteś lub czy potrzebujesz wyjaśnienia którejś komendy!
