from PIL import Image

print("----- START SILNIKA -----")

# 1. Wczytujemy pliki

lista_zdjec = ["foto1.jpg", "foto2.jpg", "foto3.jpg"]
logo = Image.open("logo.png")

# Pobieramy wymiary LOGO raz (bo są ciągle takie same)
szer_logo, wys_logo = logo.size

# PĘTLA (Taśmociąg)
for nazwa in lista_zdjec:
    print(f"Biorę na warsztat: {nazwa}")
    # 1. Otwieramy jedno zdjęcie z listy
    obraz = Image.open(nazwa)
    szer_obrazu, wys_obrazu = obraz.size

    
    # --- NOWOŚĆ: INTELIGENTNE SKALOWANIE ---
    # Chcemy, żeby logo miało np. 20% szerokości zdjęcia
    nowa_szerokosc = int(szer_obrazu * 0.20)

    # Obliczamy proporcje, żeby nie spłaszczyć logo
    wspolczynnik = nowa_szerokosc / szer_logo
    nowa_wysokosc = int(wys_logo * wspolczynnik)

    # Tworzymy zmniejszoną kopię logo
    logo_zmniejszone = logo.resize((nowa_szerokosc, nowa_szerokosc))

    # 2. Obliczamy pozycję dla tego zdjęcia
    x = szer_obrazu - nowa_szerokosc - 20
    y = wys_obrazu - nowa_wysokosc - 20
    
    # 3. Naklejamy
    obraz.paste(logo_zmniejszone, (x, y), logo_zmniejszone)
    obraz.save("gotowe_" + nazwa)
    print("✅ Zrobione!")
    
print("----- KONIEC PRACY -----")