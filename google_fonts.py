"""
Google Fonts Downloader
Moduł do pobierania i zarządzania czcionkami z Google Fonts
"""
import os
import requests
import json

FONTS_DIR = "fonts"
GOOGLE_FONTS_API_KEY = ""  # Wstaw swój klucz API Google Fonts (opcjonalnie)
CACHE_FILE = "fonts_cache.json"

if not os.path.exists(FONTS_DIR):
    os.makedirs(FONTS_DIR)

def get_popular_fonts():
    """Zwraca listę popularnych czcionek Google Fonts"""
    return [
        "Roboto", "Open Sans", "Lato", "Montserrat", "Oswald",
        "Source Sans Pro", "Raleway", "PT Sans", "Merriweather",
        "Ubuntu", "Playfair Display", "Poppins", "Nunito", "Bebas Neue",
        "Pacifico", "Dancing Script", "Anton", "Lobster", "Rubik"
    ]

def download_font(font_name):
    """Pobiera czcionkę z Google Fonts"""
    try:
        # Google Fonts CSS endpoint
        url = f"https://fonts.googleapis.com/css?family={font_name.replace(' ', '+')}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"Nie można pobrać {font_name}")
            return None
        
        # Wyciągnij URL do pliku TTF z CSS
        css_content = response.text
        font_urls = []
        for line in css_content.split('\n'):
            if 'url(' in line and '.ttf' in line:
                start = line.find('url(') + 4
                end = line.find(')', start)
                font_url = line[start:end].strip()
                if font_url.startswith('http'):
                    font_urls.append(font_url)
        
        if not font_urls:
            print(f"Brak URL dla {font_name}")
            return None
        
        # Pobierz pierwszy (regularny) wariant
        font_response = requests.get(font_urls[0], timeout=10)
        
        # Zapisz plik
        safe_name = font_name.replace(' ', '_').lower()
        font_path = os.path.join(FONTS_DIR, f"{safe_name}.ttf")
        
        with open(font_path, 'wb') as f:
            f.write(font_response.content)
        
        print(f"✓ Pobrano: {font_name}")
        return font_path
    
    except Exception as e:
        print(f"Błąd pobierania {font_name}: {e}")
        return None

def get_installed_google_fonts():
    """Zwraca listę już pobranych czcionek Google"""
    if not os.path.exists(FONTS_DIR):
        return []
    
    fonts = []
    for f in os.listdir(FONTS_DIR):
        if f.endswith('.ttf'):
            # Konwertuj nazwę pliku z powrotem na czytelną nazwę
            name = f.replace('.ttf', '').replace('_', ' ').title()
            fonts.append((name, os.path.join(FONTS_DIR, f)))
    
    return fonts

def download_popular_pack():
    """Pobiera paczkę popularnych czcionek"""
    print("Pobieranie pakietu popularnych czcionek Google Fonts...")
    popular = get_popular_fonts()
    
    for font_name in popular:
        download_font(font_name)
    
    print(f"\n✓ Pobrano {len(popular)} czcionek do folderu '{FONTS_DIR}'")

if __name__ == "__main__":
    # Test
    download_popular_pack()
