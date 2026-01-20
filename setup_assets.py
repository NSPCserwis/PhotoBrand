from PIL import Image, ImageDraw

# 1. Tworzymy udawane ZDJĘCIE
foto = Image.new('RGB', (800,600), color='red')
foto.save('foto.jpg')
print("Stworzono: foto.jpg")

# 2. Tworzymy udawane logo
logo = Image.new('RGBA', (200, 200), (0, 0, 0, 0)) # Tło przezroczyste

pedzel = ImageDraw.Draw(logo)
pedzel.ellipse([50, 50, 150, 150], fill='blue') # Rysujemy koło

logo.save('logo.png')
print("Stworzono: logo.png")