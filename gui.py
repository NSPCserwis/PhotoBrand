import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
import tkinter as tk
import os
import json
from PIL import Image, ImageTk, ImageDraw, ImageFont
import windnd
from matplotlib import font_manager
import webbrowser
import urllib.request

# --- CONFIGURATION ---
VERSION = "1.1"
UPDATE_URL = "https://raw.githubusercontent.com/NSPCserwis/PhotoBrand/main/version.txt"
LANG = "PL" # Domyślny język

TEXTS = {
    "PL": {
        "title": "Photo Brand V1.1 - ULTRA MODERN",
        "header": "🎨 PHOTO BRAND",
        "sec1": "1. PLIKI",
        "btn_files": "📂 WYBIERZ ZDJĘCIA",
        "btn_prev": "◀ Poprzednie",
        "btn_next": "Następne ▶",
        "hint_drag": "💡 Kliknij i przeciągnij logo na zdjęciu",
        "sec2": "2. WATERMARK",
        "tab_img": "OBRAZ",
        "tab_txt": "TEKST",
        "btn_browse": "BROWSE LOGO",
        "status_none": "(brak)",
        "mirror_h": "LUSTRO H",
        "mirror_v": "LUSTRO V",
        "btn_fonts": "📥 Pobierz czcionki Google Fonts",
        "sec3": "3. PARAMETRY",
        "label_size": "Wielkość:",
        "label_alpha": "Przezroczystość:",
        "label_rot": "Rotacja:",
        "sec4": "4. SZABLONY",
        "placeholder_pres": "Nazwa profilu",
        "btn_save": "ZAPISZ",
        "btn_reset": "🔄 Reset do domyślnych",
        "btn_start": "▶ START EKSPORT PRO",
        "sec5": "5. O PROGRAMIE",
        "tab_info": "INFO",
        "tab_autor": "AUTOR",
        "tab_updates": "UPDATES",
        "desc": "System do bulk-watermarkingu.",
        "btn_update": "Sprawdź aktualizacje",
        "msg_success": "Sukces",
        "msg_processed": "Oznakowano wszystkie zdjęcia!",
        "msg_del_confirm": "Czy na pewno chcesz usunąć szablon '{}'?",
        "msg_del_title": "Usuwanie",
        "msg_err_load": "Nie można wczytać profilu: {}",
        "msg_update_avail": "Dostępna nowa wersja: {}!\nObecna wersja: {}\nCzy chcesz przejść do pobierania?"
    },
    "EN": {
        "title": "Photo Brand V1.1 - ULTRA MODERN",
        "header": "🎨 PHOTO BRAND",
        "sec1": "1. FILES",
        "btn_files": "📂 SELECT PHOTOS",
        "btn_prev": "◀ Previous",
        "btn_next": "Next ▶",
        "hint_drag": "💡 Click and drag logo on the photo",
        "sec2": "2. WATERMARK",
        "tab_img": "IMAGE",
        "tab_txt": "TEXT",
        "btn_browse": "BROWSE LOGO",
        "status_none": "(none)",
        "mirror_h": "MIRROR H",
        "mirror_v": "MIRROR V",
        "btn_fonts": "📥 Download Google Fonts",
        "sec3": "3. PARAMETERS",
        "label_size": "Size:",
        "label_alpha": "Opacity:",
        "label_rot": "Rotation:",
        "sec4": "4. TEMPLATES",
        "placeholder_pres": "Profile name",
        "btn_save": "SAVE",
        "btn_reset": "🔄 Reset to defaults",
        "btn_start": "▶ START EXPORT PRO",
        "sec5": "5. ABOUT",
        "tab_info": "INFO",
        "tab_autor": "AUTHOR",
        "tab_updates": "UPDATES",
        "desc": "Bulk watermarking system.",
        "btn_update": "Check for updates",
        "msg_success": "Success",
        "msg_processed": "All photos processed!",
        "msg_del_confirm": "Are you sure you want to delete template '{}'?",
        "msg_del_title": "Deleting",
        "msg_err_load": "Cannot load profile: {}",
        "msg_update_avail": "New version available: {}!\nCurrent version: {}\nDo you want to download it?"
    }
}

print("\n" + "="*50)
print(f"  🎨 PHOTO BRAND V{VERSION} 🎨")
print("Modern UI Upgrade - Global Ready")
print("="*50 + "\n")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- STATE ---
CACHE_BG = None; CACHE_LOGO_ORIG = None; CACHE_LOGO_SM = None
PLIKI = []; CURRENT_FILE_IDX = 0; WATER_TYPE = "LOGO"; LOGO_PATH = ""
TEXT_DATA = {"txt": "MojaMarka", "col": "#00ADB5", "font": "Arial", "b": False, "i": False, "fh": False, "fv": False}
LOGO_DATA = {"fh": False, "fv": False}
REL_X, REL_Y = 0.5, 0.5; ZOOM = 1.0
PAN_X, PAN_Y = 0, 0  # Offset dla przesuwania powiększonego zdjęcia
INTERACT = {"drag": None, "sx": 0, "sy": 0, "pan_active": False, "pan_sx": 0, "pan_sy": 0}
PRESET_DIR = "presets"

if not os.path.exists(PRESET_DIR): os.makedirs(PRESET_DIR)

# --- FONT SYSTEM (RELIABLE) ---

def get_available_fonts():
    """Zwraca listę dostępnych czcionek (system + Google) z pełnymi ścieżkami"""
    font_dict = {}
    
    # 1. Czcionki systemowe (matplotlib.font_manager)
    try:
        system_fonts = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
        for font_path in system_fonts:
            try:
                # Wyciągnij nazwę czcionki
                font_prop = font_manager.FontProperties(fname=font_path)
                font_name = font_prop.get_name()
                
                # Zapisz tylko jeśli nazwa jest czytelna
                if font_name and len(font_name) > 0 and not font_name.startswith('.'):
                    # Preferuj krótsze ścieżki (często są to regularne wersje)
                    if font_name not in font_dict or len(font_path) < len(font_dict[font_name]):
                        font_dict[font_name] = font_path
            except:
                pass
    except Exception as e:
        print(f"Font scan error: {e}")
    
    # 2. Google Fonts (lokalny folder)
    google_dir = "fonts"
    if os.path.exists(google_dir):
        for f in os.listdir(google_dir):
            if f.endswith('.ttf'):
                name = f.replace('.ttf', '').replace('_', ' ').title()
                font_dict[name] = os.path.join(google_dir, f)
    
    return font_dict

FONT_CACHE = get_available_fonts()

def get_font_file(family, bold, italic):
    """Zwraca ścieżkę do pliku czcionki z uwzględnieniem Bold/Italic"""
    print(f"Requesting font: {family}, Bold={bold}, Italic={italic}")
    
    # Sprawdź cache z dokładną nazwą
    if family in FONT_CACHE:
        base_path = FONT_CACHE[family]
        
        # Próba znalezienia wariantu Bold/Italic
        if bold or italic:
            # Typowe mapowania dla popularnych czcionek
            base_name = os.path.splitext(base_path)[0]
            
            # Próbuj różne kombinacje
            if bold and italic:
                variants = [base_name + "bi.ttf", base_name + "z.ttf", base_name + "-BoldItalic.ttf"]
            elif bold:
                variants = [base_name + "bd.ttf", base_name + "b.ttf", base_name + "-Bold.ttf"]
            elif italic:
                variants = [base_name + "i.ttf", base_name + "-Italic.ttf"]
            else:
                variants = []
            
            # Spróbuj znaleźć wariant
            for variant_path in variants:
                if os.path.exists(variant_path):
                    print(f"✓ Found variant: {variant_path}")
                    return variant_path
            
            # Jeśli nie ma wariantu, użyj regularnego
            print(f"⚠ No {['', 'Bold'][bold]}{['', 'Italic'][italic]} variant, using regular")
        
        print(f"✓ Using: {base_path}")
        return base_path
    
    # Fallback do Arial
    if "Arial" in FONT_CACHE:
        print(f"⚠ Font '{family}' not found, using Arial")
        arial_path = FONT_CACHE["Arial"]
        
        # Próba znalezienia Arial Bold/Italic
        if bold or italic:
            arial_dir = "C:\\Windows\\Fonts\\"
            if bold and italic:
                variant = arial_dir + "arialbi.ttf"
            elif bold:
                variant = arial_dir + "arialbd.ttf"
            elif italic:
                variant = arial_dir + "ariali.ttf"
            else:
                variant = arial_path
            
            if os.path.exists(variant):
                return variant
        
        return arial_path
    
    # Last resort
    fallback = "C:\\Windows\\Fonts\\arial.ttf"
    print(f"⚠ Using fallback: {fallback}")
    return fallback

# --- CORE ENGINE ---

def update_asset(event=None):
    """Generuje znak wodny bez utraty jakości (Smart Scaling)."""
    global CACHE_LOGO_ORIG, CACHE_LOGO_SM
    
    if not CACHE_BG:
        return  # Nie ma tła, nie ma co renderować
    
    bw = CACHE_BG.width
    target_px = max(10, int(bw * (var_scale.get()/100.0)))
    
    if WATER_TYPE == "TEXT":
        txt = var_text.get() or " "
        try:
            # Używamy wartości z TEXT_DATA zamiast bezpośrednio z widgetów
            f_path = get_font_file(TEXT_DATA["font"], TEXT_DATA["b"], TEXT_DATA["i"])
            
            # Render testowy dla ratio
            try: test_font = ImageFont.truetype(f_path, 100)
            except: test_font = ImageFont.load_default()
            
            d_tmp = ImageDraw.Draw(Image.new('RGBA', (1,1)))
            l, t, r, b = d_tmp.textbbox((0, 0), txt, font=test_font)
            ratio = 100 / (r - l) if (r-l) > 0 else 1
            
            # Finalny render ostrej czcionki
            final_font_size = int(target_px * ratio)
            try: p_font = ImageFont.truetype(f_path, final_font_size)
            except: p_font = ImageFont.load_default()
            
            l, t, r, b = d_tmp.textbbox((0, 0), txt, font=p_font)
            img = Image.new('RGBA', (r-l+40, b-t+40), (0,0,0,0))
            ImageDraw.Draw(img).text((20, 20), txt, font=p_font, fill=TEXT_DATA["col"])
            CACHE_LOGO_ORIG = img
            CACHE_LOGO_SM = img # Tekst jest już w docelowej skali
        except Exception as e:
            print(f"Text render error: {e}")
            CACHE_LOGO_ORIG = None
    else:
        if CACHE_LOGO_ORIG:
            th = int(CACHE_LOGO_ORIG.height * (target_px / CACHE_LOGO_ORIG.width))
            CACHE_LOGO_SM = CACHE_LOGO_ORIG.resize((target_px, th), Image.BILINEAR)

    var_px.set(str(CACHE_LOGO_SM.width if CACHE_LOGO_SM else 0))
    render_view()  # KRYTYCZNE: Wywołaj render aby zobaczyć zmiany!

def render_view(event=None):
    canv.delete("all")
    cw, ch = canv.winfo_width(), canv.winfo_height()
    if cw < 100: cw, ch = 1200, 800
    
    if CACHE_BG:
        canv.img_bg = ImageTk.PhotoImage(CACHE_BG)
        # Zastosowanie offsetu Pan dla powiększonego zdjęcia
        canv.create_image(cw//2 + PAN_X, ch//2 + PAN_Y, image=canv.img_bg, anchor="center")
    
    if CACHE_LOGO_SM and CACHE_BG:
        w = CACHE_LOGO_SM.copy()
        # Niezależne ustawienia odbić
        if WATER_TYPE == "LOGO":
            fh, fv = var_fh_l.get(), var_fv_l.get()
        else:
            fh, fv = var_fh_t.get(), var_fv_t.get()
            
        if fh: w = w.transpose(Image.FLIP_LEFT_RIGHT)
        if fv: w = w.transpose(Image.FLIP_TOP_BOTTOM)
        
        a = var_rot.get()
        if a != 0: w = w.rotate(-a, expand=True, resample=Image.BILINEAR)
        
        op = var_opacity.get()
        if op < 100: w.putalpha(w.getchannel("A").point(lambda p: p * (op/100)))
        
        bw, bh = CACHE_BG.width, CACHE_BG.height
        # Offset tła z uwzględnieniem Pan
        ox, oy = (cw-bw)//2 + PAN_X, (ch-bh)//2 + PAN_Y
        canv.img_l = ImageTk.PhotoImage(w)
        # REL_X/Y trzymają pozycję stabilnie
        canv.create_image(ox + int(REL_X*bw), oy + int(REL_Y*bh), image=canv.img_l, anchor="nw", tags="l")

# --- UI ACTIONS ---

def cmd_load_files(paths=None):
    p = paths if paths else filedialog.askopenfilenames(filetypes=[("Obrazy", "*.jpg;*.png;*.webp;*.bmp;*.tiff;*.jpeg")])
    if p:
        # Sortowanie zdjęć
        valid = [f for f in p if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff'))]
        if not valid: return
        global PLIKI, CURRENT_FILE_IDX; PLIKI = valid; CURRENT_FILE_IDX = 0
        update_file_label()
        cmd_update_bg()

def cmd_update_bg():
    global CACHE_BG, PAN_X, PAN_Y
    if not PLIKI: return
    # Reset Pan przy zmianie zdjęcia
    PAN_X, PAN_Y = 0, 0
    cw, ch = canv.winfo_width(), canv.winfo_height()
    if cw < 100: cw, ch = 1200, 800
    i = Image.open(PLIKI[CURRENT_FILE_IDX]).convert("RGBA")
    # Tło skalujemy ZOOMem
    i.thumbnail((int((cw-60)*ZOOM), int((ch-60)*ZOOM)))
    CACHE_BG = i; update_asset()

def update_file_label():
    """Aktualizuje etykietę z liczbą plików i nawigacją"""
    if PLIKI:
        btn_files.configure(text=f"📂 {len(PLIKI)} plików (podgląd: {CURRENT_FILE_IDX+1}/{len(PLIKI)})")
        btn_prev.configure(state="normal" if CURRENT_FILE_IDX > 0 else "disabled")
        btn_next.configure(state="normal" if CURRENT_FILE_IDX < len(PLIKI)-1 else "disabled")

def cmd_prev_file():
    global CURRENT_FILE_IDX
    if CURRENT_FILE_IDX > 0:
        CURRENT_FILE_IDX -= 1
        update_file_label()
        cmd_update_bg()

def cmd_next_file():
    global CURRENT_FILE_IDX
    if CURRENT_FILE_IDX < len(PLIKI) - 1:
        CURRENT_FILE_IDX += 1
        update_file_label()
        cmd_update_bg()

def on_os_drop(files):
    # Obsługa Drag & Drop z folderu
    f_list = [f.decode('gbk') if isinstance(f, bytes) else f for f in files]
    cmd_load_files(f_list)

def cmd_save_preset():
    n = var_pres_name.get() or "Profil"
    d = {"t": var_text.get(), "c": TEXT_DATA["col"], "s": var_scale.get(), "o": var_opacity.get(), "r": var_rot.get(), "f": cb_font.get(), "b": var_bold.get(), "i": var_italic.get()}
    with open(os.path.join(PRESET_DIR, f"{n}.json"), 'w') as f: json.dump(d, f)
    refresh_list()

def reset_to_defaults():
    """Przywraca domyślne ustawienia"""
    TEXT_DATA["txt"] = "PhotoBrand"
    TEXT_DATA["col"] = "#00ADB5"
    TEXT_DATA["font"] = "Arial"
    TEXT_DATA["b"] = False
    TEXT_DATA["i"] = False
    
    var_text.set(TEXT_DATA["txt"])
    var_scale.set(20)
    var_opacity.set(100)
    var_rot.set(0)
    cb_font.set(TEXT_DATA["font"])
    var_bold.set(False)
    var_italic.set(False)
    var_fh_l.set(False)
    var_fv_l.set(False)
    var_fh_t.set(False)
    var_fv_t.set(False)
    btn_col.configure(fg_color=TEXT_DATA["col"])
    
    global REL_X, REL_Y, ZOOM, PAN_X, PAN_Y
    REL_X, REL_Y = 0.5, 0.5
    ZOOM = 1.0
    PAN_X, PAN_Y = 0, 0
    
    if CACHE_BG:
        cmd_update_bg()
    else:
        update_asset()

def refresh_list():
    """Odświeża listę szablonów (przyciski CTk)"""
    try:
        for child in f_presets.winfo_children(): child.destroy()
        if os.path.exists(PRESET_DIR):
            for f in sorted(os.listdir(PRESET_DIR)):
                if f.endswith(".json"):
                    name = f.replace(".json", "")
                    btn = ctk.CTkButton(f_presets, text=name, fg_color="transparent", text_color="#ccc", anchor="w",
                                       command=lambda n=name: [var_pres_name.set(n), on_preset_load_direct(n)])
                    btn.pack(fill="x")
    except NameError: pass # f_presets może nie być jeszcze stworzone

def on_preset_load_direct(name):
    """Wczytuje profil bezpośrednio po nazwie"""
    try:
        with open(os.path.join(PRESET_DIR, f"{name}.json"), 'r') as f:
            p = json.load(f)
            TEXT_DATA["txt"] = p.get("t", "PhotoBrand")
            TEXT_DATA["col"] = p.get("c", "#00ADB5")
            TEXT_DATA["font"] = p.get("f", "Arial")
            TEXT_DATA["b"] = p.get("b", False)
            TEXT_DATA["i"] = p.get("i", False)
            var_text.set(TEXT_DATA["txt"])
            var_scale.set(p.get("s", 20))
            var_opacity.set(p.get("o", 100))
            var_rot.set(p.get("r", 0))
            cb_font.set(TEXT_DATA["font"])
            var_bold.set(TEXT_DATA["b"])
            var_italic.set(TEXT_DATA["i"])
            btn_col.configure(fg_color=TEXT_DATA["col"])
            update_asset()
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można wczytać profilu: {e}")

def on_preset_load(e):
    """Wczytuje profil z listy"""
    if not lb_presets.curselection(): return
    try:
        with open(os.path.join(PRESET_DIR, f"{lb_presets.get(lb_presets.curselection())}.json"), 'r') as f:
            p = json.load(f)
            # Aktualizuj TEXT_DATA
            TEXT_DATA["txt"] = p.get("t", "PhotoBrand")
            TEXT_DATA["col"] = p.get("c", "#00ADB5")
            TEXT_DATA["font"] = p.get("f", "Arial")
            TEXT_DATA["b"] = p.get("b", False)
            TEXT_DATA["i"] = p.get("i", False)
            
            # Aktualizuj UI
            var_text.set(TEXT_DATA["txt"])
            var_scale.set(p.get("s", 20))
            var_opacity.set(p.get("o", 100))
            var_rot.set(p.get("r", 0))
            cb_font.set(TEXT_DATA["font"])
            var_bold.set(TEXT_DATA["b"])
            var_italic.set(TEXT_DATA["i"])
            btn_col.config(bg=TEXT_DATA["col"])
            update_asset()
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można wczytać profilu: {e}")

def run_export():
    if not PLIKI or CACHE_LOGO_ORIG is None: return
    out = os.path.join(os.path.dirname(PLIKI[0]), "PhotoBrand_V15_PRO")
    if not os.path.exists(out): os.mkdir(out)
    
    for path in PLIKI:
        img = Image.open(path).convert("RGBA")
        W, H = img.size
        # Scalable sharp text
        if WATER_TYPE == "TEXT":
            t_px = int(W * (var_scale.get()/100.0))
            # Używamy TEXT_DATA zamiast widgetów
            f_path = get_font_file(TEXT_DATA["font"], TEXT_DATA["b"], TEXT_DATA["i"])
            d_t = ImageDraw.Draw(Image.new('RGBA', (1,1)))
            test_f = ImageFont.truetype(f_path, 100)
            l, t, r, b = d_t.textbbox((0,0), var_text.get(), font=test_f)
            f_res = int(t_px * (100/(r-l)))
            p_f = ImageFont.truetype(f_path, f_res)
            l, t, r, b = d_t.textbbox((0,0), var_text.get(), font=p_f)
            wm = Image.new('RGBA', (r-l+40, b-t+40), (0,0,0,0))
            ImageDraw.Draw(wm).text((20, 20), var_text.get(), font=p_f, fill=TEXT_DATA["col"])
        else:
            t_px = int(W * (var_scale.get()/100.0))
            wm = CACHE_LOGO_ORIG.resize((t_px, int(CACHE_LOGO_ORIG.height*(t_px/CACHE_LOGO_ORIG.width))), Image.LANCZOS)
        
        fh = var_fh_l.get() if WATER_TYPE=="LOGO" else var_fh_t.get()
        fv = var_fv_l.get() if WATER_TYPE=="LOGO" else var_fv_t.get()
        if fh: wm = wm.transpose(Image.FLIP_LEFT_RIGHT)
        if fv: wm = wm.transpose(Image.FLIP_TOP_BOTTOM)
        if var_rot.get() != 0: wm = wm.rotate(-var_rot.get(), expand=True, resample=Image.BICUBIC)
        if var_opacity.get() < 100: wm.putalpha(wm.getchannel("A").point(lambda p: p * (var_opacity.get()/100)))

        img.paste(wm, (int(REL_X*W), int(REL_Y*H)), wm)
        if os.path.splitext(path)[1].lower() in ['.jpg', '.jpeg']: img = img.convert("RGB")
        img.save(os.path.join(out, os.path.basename(path)), quality=95)
    messagebox.showinfo("Success", "Oznakowano wszystkie zdjęcia!")

# --- CUSTOM TKINTER GUI SETUP ---
root = ctk.CTk()
root.title("Photo Brand V1.0 - ULTRA MODERN")
root.geometry("1400x900")

# --- VARS ---
var_text = tk.StringVar(value="LogoMark"); var_scale = tk.DoubleVar(value=20); var_opacity = tk.DoubleVar(value=100)
var_rot = tk.IntVar(value=0); var_px = tk.StringVar(value="200"); var_bold = tk.BooleanVar(); var_italic = tk.BooleanVar()
var_fh_l = tk.BooleanVar(); var_fv_l = tk.BooleanVar(); var_fh_t = tk.BooleanVar(); var_fv_t = tk.BooleanVar()
var_pres_name = tk.StringVar(value="Nowy_Profil")

# Główna struktura (Grid zamiast PanedWindow dla lepszej kontroli w CTk)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Sidebar (Przewijalny) - ZWĘŻONY DO 300px
p_l_inner = ctk.CTkScrollableFrame(root, width=300, corner_radius=0, fg_color="#1a1a1a")
p_l_inner.grid(row=0, column=0, sticky="nsew")

# Prawy Panel (Podgląd)
p_r = ctk.CTkFrame(root, corner_radius=0, fg_color="#000000")
p_r.grid(row=0, column=1, sticky="nsew")

canv = tk.Canvas(p_r, bg="#000000", highlightthickness=0)
canv.pack(fill="both", expand=True)

lbl_header = ctk.CTkLabel(p_l_inner, text=TEXTS[LANG]["header"], font=("Segoe UI", 24, "bold"), text_color="#00D2FF")
lbl_header.pack(pady=(10,20), anchor="w")

# 1. PLIKI
sec1 = ctk.CTkFrame(p_l_inner, corner_radius=10)
sec1.pack(fill="x", pady=2, padx=12) 
lbl_sec1 = ctk.CTkLabel(sec1, text=TEXTS[LANG]["sec1"], font=("Segoe UI", 11, "bold"))
lbl_sec1.pack(pady=2, padx=10, anchor="w")

btn_files = ctk.CTkButton(sec1, text=TEXTS[LANG]["btn_files"], command=cmd_load_files, fg_color="#3b82f6", hover_color="#2563eb", height=32)
btn_files.pack(fill="x", padx=10, pady=2)

# Nawigacja między plikami
f_nav = ctk.CTkFrame(sec1, fg_color="transparent")
f_nav.pack(fill="x", pady=2, padx=10)
btn_prev = ctk.CTkButton(f_nav, text=TEXTS[LANG]["btn_prev"], command=cmd_prev_file, state="disabled", fg_color="#4b5563", height=28)
btn_prev.pack(side="left", expand=True, fill="x", padx=2)
btn_next = ctk.CTkButton(f_nav, text=TEXTS[LANG]["btn_next"], command=cmd_next_file, state="disabled", fg_color="#4b5563", height=28)
btn_next.pack(side="right", expand=True, fill="x", padx=2)
lbl_hint = ctk.CTkLabel(sec1, text=TEXTS[LANG]["hint_drag"], text_color="#888", font=("Segoe UI", 10))
lbl_hint.pack(pady=2)

# 2. ZNAK
sec2 = ctk.CTkFrame(p_l_inner, corner_radius=10)
sec2.pack(fill="x", pady=4, padx=12)
lbl_sec2 = ctk.CTkLabel(sec2, text=TEXTS[LANG]["sec2"], font=("Segoe UI", 11, "bold"))
lbl_sec2.pack(pady=2, padx=10, anchor="w")

tab_water = ctk.CTkTabview(sec2, height=130)
tab_water.pack(fill="x", padx=10, pady=(0,5))
tab_water.add("OBRAZ")
tab_water.add("TEKST")
# Ustawienie początkowych nazw zakładek (wymienionych w refresh_ui)
tab_water._segmented_button._buttons_dict["OBRAZ"].configure(text=TEXTS[LANG]["tab_img"])
tab_water._segmented_button._buttons_dict["TEKST"].configure(text=TEXTS[LANG]["tab_txt"])

# Tab Logo
t_logo = tab_water.tab("OBRAZ")

def cmd_load_logo():
    global LOGO_PATH, CACHE_LOGO_ORIG, WATER_TYPE
    p = filedialog.askopenfilename(filetypes=[("Obrazy", "*.jpg;*.png;*.webp;*.bmp;*.tiff;*.jpeg")])
    if p:
        LOGO_PATH = p
        WATER_TYPE = "LOGO"
        CACHE_LOGO_ORIG = Image.open(p).convert("RGBA")
        btn_logo_status.configure(text=f"✓ {os.path.basename(p)[:20]}...")
        update_asset()

btn_browse = ctk.CTkButton(t_logo, text=TEXTS[LANG]["btn_browse"], command=cmd_load_logo, height=28)
btn_browse.pack(fill="x", pady=2)
btn_logo_status = ctk.CTkLabel(t_logo, text=TEXTS[LANG]["status_none"], text_color="#666", font=("Segoe UI", 10))
btn_logo_status.pack(pady=0)
fl_l = ctk.CTkFrame(t_logo, fg_color="transparent")
fl_l.pack(fill="x", pady=2)
cb_mirror_h_l = ctk.CTkCheckBox(fl_l, text=TEXTS[LANG]["mirror_h"], variable=var_fh_l, command=render_view, font=("Segoe UI", 10))
cb_mirror_h_l.pack(side="left", padx=5)
cb_mirror_v_l = ctk.CTkCheckBox(fl_l, text=TEXTS[LANG]["mirror_v"], variable=var_fv_l, command=render_view, font=("Segoe UI", 10))
cb_mirror_v_l.pack(side="left", padx=5)

# Tab Tekst
t_text = tab_water.tab("TEKST")
ent_text = ctk.CTkEntry(t_text, textvariable=var_text, font=("Segoe UI", 12))
ent_text.pack(fill="x", pady=5)
var_text.trace_add("write", lambda *a: update_asset())
ff = ctk.CTkFrame(t_text, fg_color="transparent")
ff.pack(fill="x", pady=5)

# Lista czcionek - Zwężona
font_names = sorted(list(FONT_CACHE.keys()))
cb_font = ctk.CTkOptionMenu(ff, values=font_names, command=lambda v: [TEXT_DATA.__setitem__("font", v), update_asset()], width=140)
cb_font.set(TEXT_DATA["font"] if TEXT_DATA["font"] in font_names else "Arial")
cb_font.pack(side="left", padx=2)

def cmd_change_color():
    c = colorchooser.askcolor(initialcolor=TEXT_DATA["col"])[1]
    if c:
        TEXT_DATA["col"] = c
        btn_col.configure(fg_color=c)
        update_asset()

btn_col = ctk.CTkButton(ff, width=30, height=30, text="", fg_color=TEXT_DATA["col"], corner_radius=15, command=cmd_change_color)
btn_col.pack(side="right", padx=5)

fs = ctk.CTkFrame(t_text, fg_color="transparent")
fs.pack(fill="x", pady=5)
ctk.CTkCheckBox(fs, text="BOLD", variable=var_bold, command=lambda: [TEXT_DATA.__setitem__("b", var_bold.get()), update_asset()]).pack(side="left", padx=5)
ctk.CTkCheckBox(fs, text="ITALIC", variable=var_italic, command=lambda: [TEXT_DATA.__setitem__("i", var_italic.get()), update_asset()]).pack(side="left", padx=5)

fl_t = ctk.CTkFrame(t_text, fg_color="transparent")
fl_t.pack(fill="x", pady=5)
cb_mirror_h_t = ctk.CTkCheckBox(fl_t, text=TEXTS[LANG]["mirror_h"], variable=var_fh_t, command=render_view)
cb_mirror_h_t.pack(side="left", padx=5)
cb_mirror_v_t = ctk.CTkCheckBox(fl_t, text=TEXTS[LANG]["mirror_v"], variable=var_fv_t, command=render_view)
cb_mirror_v_t.pack(side="left", padx=5)

tab_water.configure(command=lambda: [globals().update(WATER_TYPE="LOGO" if tab_water.get()=="OBRAZ" else "TEXT"), update_asset()])

# Przycisk Google Fonts
def cmd_download_fonts():
    """Pobiera popularne czcionki Google Fonts"""
    try:
        import google_fonts
        google_fonts.download_popular_pack()
        # Odśwież listę czcionek
        refresh_font_list()
        messagebox.showinfo("Sukces", "Pobrano 19 profesjonalnych czcionek Google Fonts!\nSprawdź folder 'fonts/'")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można pobrać czcionek: {e}")

def refresh_font_list():
    """Odświeża listę czcionek"""
    global FONT_CACHE
    FONT_CACHE = get_available_fonts()
    font_names = sorted(list(FONT_CACHE.keys()))
    cb_font.configure(values=font_names)
    print(f"Refreshed font list: {len(font_names)} fonts available")

# Przycisk Google Fonts (zmieniony na CTk)
btn_google_fonts = ctk.CTkButton(t_text, text=TEXTS[LANG]["btn_fonts"], 
              command=cmd_download_fonts, fg_color="#4b5563", hover_color="#374151", height=28)
btn_google_fonts.pack(fill="x", pady=5)

# 3. PARAMETRY
sec3 = ctk.CTkFrame(p_l_inner, corner_radius=10)
sec3.pack(fill="x", pady=4, padx=12)
lbl_sec3 = ctk.CTkLabel(sec3, text=TEXTS[LANG]["sec3"], font=("Segoe UI", 11, "bold"))
lbl_sec3.pack(pady=2, padx=10, anchor="w")

# Suwak wielkości
f_label_px = ctk.CTkFrame(sec3, fg_color="transparent")
f_label_px.pack(fill="x", padx=10)
lbl_size = ctk.CTkLabel(f_label_px, text=TEXTS[LANG]["label_size"], font=("Segoe UI", 11))
lbl_size.pack(side="left")
ent_px = ctk.CTkEntry(f_label_px, textvariable=var_px, width=50, font=("Segoe UI", 10, "bold"), height=24)
ent_px.pack(side="left", padx=5)
ent_px.bind("<Return>", lambda e: [var_scale.set((float(var_px.get())/(CACHE_BG.width if CACHE_BG else 1))*100), update_asset()])

slider_scale = ctk.CTkSlider(sec3, from_=1, to=100, variable=var_scale, command=lambda v: update_asset(), height=16)
slider_scale.pack(fill="x", padx=15, pady=2)

# Suwak przezroczystości
lbl_alpha = ctk.CTkLabel(sec3, text=TEXTS[LANG]["label_alpha"], font=("Segoe UI", 11))
lbl_alpha.pack(anchor="w", padx=12, pady=(2,0))
slider_opacity = ctk.CTkSlider(sec3, from_=5, to=100, variable=var_opacity, command=lambda v: render_view(), height=16)
slider_opacity.pack(fill="x", padx=15, pady=2)

# Suwak rotacji
lbl_rot = ctk.CTkLabel(sec3, text=TEXTS[LANG]["label_rot"], font=("Segoe UI", 11))
lbl_rot.pack(anchor="w", padx=12, pady=(2,0))
slider_rot = ctk.CTkSlider(sec3, from_=0, to=360, variable=var_rot, command=lambda v: render_view(), number_of_steps=360, height=16)
slider_rot.pack(fill="x", padx=15, pady=2)

# 4. SZABLONY
sec4 = ctk.CTkFrame(p_l_inner, corner_radius=10)
sec4.pack(fill="x", pady=4, padx=12)
lbl_sec4 = ctk.CTkLabel(sec4, text=TEXTS[LANG]["sec4"], font=("Segoe UI", 12, "bold"))
lbl_sec4.pack(pady=5, padx=10, anchor="w")

# Custom Scrollable List for Presets
f_presets = ctk.CTkScrollableFrame(sec4, height=100)
f_presets.pack(fill="x", padx=10, pady=5)

def cmd_delete_preset(name):
    """Usuwa plik szablonu i odświeża listę"""
    if messagebox.askyesno("Usuwanie", f"Czy na pewno chcesz usunąć szablon '{name}'?"):
        try:
            path = os.path.join(PRESET_DIR, f"{name}.json")
            if os.path.exists(path):
                os.remove(path)
                refresh_list()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się usunąć pliku: {e}")

def refresh_list():
    """Odświeża listę szablonów (przyciski CTk z opcją usuwania)"""
    try:
        for child in f_presets.winfo_children(): child.destroy()
        if os.path.exists(PRESET_DIR):
            for f in sorted(os.listdir(PRESET_DIR)):
                if f.endswith(".json"):
                    name = f.replace(".json", "")
                    f_item = ctk.CTkFrame(f_presets, fg_color="transparent")
                    f_item.pack(fill="x", pady=1)
                    
                    btn_load = ctk.CTkButton(f_item, text=name, fg_color="transparent", text_color="#ccc", anchor="w",
                                       height=24, font=("Segoe UI", 10),
                                       command=lambda n=name: [var_pres_name.set(n), on_preset_load_direct(n)])
                    btn_load.pack(side="left", fill="x", expand=True)
                    
                    btn_del = ctk.CTkButton(f_item, text="❌", width=20, height=20, fg_color="transparent", 
                                           text_color="#555", hover_color="#ef4444",
                                           command=lambda n=name: cmd_delete_preset(n))
                    btn_del.pack(side="right", padx=2)
    except NameError: pass 

def on_preset_load_direct(name):
    # Wczytuje profil bezpośrednio
    try:
        with open(os.path.join(PRESET_DIR, f"{name}.json"), 'r') as f:
            p = json.load(f)
            TEXT_DATA["txt"] = p.get("t", "PhotoBrand")
            TEXT_DATA["col"] = p.get("c", "#00ADB5")
            TEXT_DATA["font"] = p.get("f", "Arial")
            TEXT_DATA["b"] = p.get("b", False)
            TEXT_DATA["i"] = p.get("i", False)
            var_text.set(TEXT_DATA["txt"])
            var_scale.set(p.get("s", 20))
            var_opacity.set(p.get("o", 100))
            var_rot.set(p.get("r", 0))
            cb_font.set(TEXT_DATA["font"])
            var_bold.set(TEXT_DATA["b"])
            var_italic.set(TEXT_DATA["i"])
            btn_col.configure(fg_color=TEXT_DATA["col"])
            update_asset()
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można wczytać profilu: {e}")

f_p = ctk.CTkFrame(sec4, fg_color="transparent")
f_p.pack(fill="x", pady=2, padx=10)
ent_pres = ctk.CTkEntry(f_p, textvariable=var_pres_name, placeholder_text=TEXTS[LANG]["placeholder_pres"], height=28, font=("Segoe UI", 10))
ent_pres.pack(side="left", fill="x", expand=True)
btn_pres_save = ctk.CTkButton(f_p, text=TEXTS[LANG]["btn_save"], width=60, height=28, command=cmd_save_preset)
btn_pres_save.pack(side="right", padx=5)

btn_reset_def = ctk.CTkButton(sec4, text=TEXTS[LANG]["btn_reset"], command=reset_to_defaults, fg_color="#ef4444", hover_color="#dc2626", height=28)
btn_reset_def.pack(fill="x", padx=10, pady=5)
refresh_list()

btn_start_export = ctk.CTkButton(p_l_inner, text=TEXTS[LANG]["btn_start"], command=run_export, fg_color="#10b981", hover_color="#059669", height=42, font=("Segoe UI", 12, "bold"))
btn_start_export.pack(fill="x", pady=10, padx=20)

# 5. O PROGRAMIE
sec5 = ctk.CTkFrame(p_l_inner, corner_radius=10)
sec5.pack(fill="x", pady=4, padx=12)
lbl_sec5 = ctk.CTkLabel(sec5, text=TEXTS[LANG]["sec5"], font=("Segoe UI", 11, "bold"))
lbl_sec5.pack(pady=2, padx=10, anchor="w")

tab_info = ctk.CTkTabview(sec5, height=110) # Zmniejszony height
tab_info.pack(fill="x", padx=10, pady=(0,5))
tab_info.add("INFO")
tab_info.add("AUTOR")
tab_info.add("UPDATES")

# Tab Info
t_i = tab_info.tab("INFO")
lbl_info_v = ctk.CTkLabel(t_i, text="Photo Brand V"+VERSION, font=("Segoe UI", 11, "bold"))
lbl_info_v.pack(anchor="w")
lbl_info_d = ctk.CTkLabel(t_i, text=TEXTS[LANG]["desc"], font=("Segoe UI", 10))
lbl_info_d.pack(anchor="w")

# Przełącznik języka
f_lang = ctk.CTkFrame(t_i, fg_color="transparent")
f_lang.pack(fill="x", pady=5)
def set_lang(l):
    global LANG
    LANG = l
    refresh_ui()

ctk.CTkButton(f_lang, text="Polski 🇵🇱", width=60, height=22, font=("Segoe UI", 10), command=lambda: set_lang("PL")).pack(side="left", padx=2)
ctk.CTkButton(f_lang, text="English 🇬🇧", width=60, height=22, font=("Segoe UI", 10), command=lambda: set_lang("EN")).pack(side="left", padx=2)

def refresh_ui():
    """Odświeża teksty w całym interfejsie po zmianie języka."""
    root.title(TEXTS[LANG]["title"])
    lbl_header.configure(text=TEXTS[LANG]["header"])
    lbl_sec1.configure(text=TEXTS[LANG]["sec1"])
    btn_files.configure(text=TEXTS[LANG]["btn_files"])
    btn_prev.configure(text=TEXTS[LANG]["btn_prev"])
    btn_next.configure(text=TEXTS[LANG]["btn_next"])
    lbl_hint.configure(text=TEXTS[LANG]["hint_drag"])
    lbl_sec2.configure(text=TEXTS[LANG]["sec2"])
    
    # Zakładki Watermark
    tab_water._segmented_button._buttons_dict["OBRAZ"].configure(text=TEXTS[LANG]["tab_img"])
    tab_water._segmented_button._buttons_dict["TEKST"].configure(text=TEXTS[LANG]["tab_txt"])
    
    btn_browse.configure(text=TEXTS[LANG]["btn_browse"])
    if not CACHE_LOGO_ORIG: btn_logo_status.configure(text=TEXTS[LANG]["status_none"])
    cb_mirror_h_l.configure(text=TEXTS[LANG]["mirror_h"])
    cb_mirror_v_l.configure(text=TEXTS[LANG]["mirror_v"])
    cb_mirror_h_t.configure(text=TEXTS[LANG]["mirror_h"])
    cb_mirror_v_t.configure(text=TEXTS[LANG]["mirror_v"])
    btn_google_fonts.configure(text=TEXTS[LANG]["btn_fonts"])
    
    lbl_sec3.configure(text=TEXTS[LANG]["sec3"])
    lbl_size.configure(text=TEXTS[LANG]["label_size"])
    lbl_alpha.configure(text=TEXTS[LANG]["label_alpha"])
    lbl_rot.configure(text=TEXTS[LANG]["label_rot"])
    
    lbl_sec4.configure(text=TEXTS[LANG]["sec4"])
    ent_pres.configure(placeholder_text=TEXTS[LANG]["placeholder_pres"])
    btn_pres_save.configure(text=TEXTS[LANG]["btn_save"])
    btn_reset_def.configure(text=TEXTS[LANG]["btn_reset"])
    btn_start_export.configure(text=TEXTS[LANG]["btn_start"])
    
    lbl_sec5.configure(text=TEXTS[LANG]["sec5"])
    tab_info._segmented_button._buttons_dict["INFO"].configure(text=TEXTS[LANG]["tab_info"])
    tab_info._segmented_button._buttons_dict["AUTOR"].configure(text=TEXTS[LANG]["tab_autor"])
    tab_info._segmented_button._buttons_dict["UPDATES"].configure(text=TEXTS[LANG]["tab_updates"])
    
    lbl_info_d.configure(text=TEXTS[LANG]["desc"])
    btn_update_check.configure(text=TEXTS[LANG]["btn_update"])
    update_file_label() # Odśwież info o plikach

# Tab Autor
t_a = tab_info.tab("AUTOR")
ctk.CTkLabel(t_a, text="Powered by NSPC", text_color="#00D2FF", font=("Segoe UI", 11, "bold")).pack(anchor="w")

# Funkcje otwierania linków
def open_url(url): webbrowser.open(url)

f_links = ctk.CTkFrame(t_a, fg_color="transparent")
f_links.pack(fill="x", pady=2)

# Facebook
l_fb = ctk.CTkLabel(f_links, text="Facebook", text_color="#3b82f6", cursor="hand2", font=("Segoe UI", 10, "underline"))
l_fb.pack(side="left", padx=2); l_fb.bind("<Button-1>", lambda e: open_url("https://www.facebook.com/nspcserwis/"))

# GitHub
l_gh = ctk.CTkLabel(f_links, text="GitHub", text_color="#3b82f6", cursor="hand2", font=("Segoe UI", 10, "underline"))
l_gh.pack(side="left", padx=5); l_gh.bind("<Button-1>", lambda e: open_url("https://github.com/NSPCserwis"))

# WWW
l_web = ctk.CTkLabel(f_links, text="NSPC Site", text_color="#3b82f6", cursor="hand2", font=("Segoe UI", 10, "underline"))
l_web.pack(side="left", padx=2); l_web.bind("<Button-1>", lambda e: open_url("https://nspcserwis.wixsite.com/nspc"))

# Tab Updates
t_u = tab_info.tab("UPDATES")

def check_updates_real():
    """Pobiera wersję z serwera i porównuje z lokalną"""
    try:
        # Odczyt wersji z sieci (timeout 5s)
        with urllib.request.urlopen(UPDATE_URL, timeout=5) as response:
            server_version = response.read().decode('utf-8').strip()
        
        if server_version > VERSION:
            if messagebox.askyesno("Aktualizacja", f"Dostępna nowa wersja: {server_version}!\nObecna wersja: {VERSION}\nCzy chcesz przejść do pobierania?"):
                webbrowser.open("https://github.com/NSPCserwis/PhotoBrand/releases/tag/v1.0") # Tu też możesz dać link do downloadu
        else:
            messagebox.showinfo("Aktualizacja", f"Posiadasz najnowszą wersję ({VERSION}).")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można połączyć się z serwerem aktualizacji.\nSprawdź połączenie z internetem.")

btn_update_check = ctk.CTkButton(t_u, text=TEXTS[LANG]["btn_update"], command=check_updates_real, height=28)
btn_update_check.pack(fill="x", pady=5)

# PRAWY PANEL (podgląd jest już zdefiniowany wcześniej)

# INTERAKCJA
def on_scr(e):
    items = canv.find_closest(e.x, e.y)
    if items:
        item = items[0]
        if "l" in canv.gettags(item):
            var_scale.set(max(1, min(var_scale.get()*(1.1 if e.delta>0 else 0.9), 100))); update_asset()
            return
    
    global ZOOM, PAN_X, PAN_Y
    ZOOM = max(0.2, min(ZOOM*(1.1 if e.delta>0 else 0.9), 5.0))
    PAN_X, PAN_Y = 0, 0
    cmd_update_bg()

def on_lpm_down(e):
    """Obsługa LPM: Ctrl+LPM = Pan, zwykły LPM = przeciągnij logo"""
    if e.state & 0x0004:  # CTRL
        INTERACT["pan_active"] = True
        INTERACT["pan_sx"], INTERACT["pan_sy"] = e.x, e.y
    else:
        # Zwykłe przeciąganie logo - bezpieczne sprawdzenie
        items = canv.find_closest(e.x, e.y)
        if items:
            item = items[0]
            if "l" in canv.gettags(item):
                INTERACT["drag"] = item
                INTERACT["sx"], INTERACT["sy"] = e.x, e.y

def on_lpm_motion(e):
    """Obsługa ruchu LPM: Pan lub przeciąganie logo"""
    global PAN_X, PAN_Y, REL_X, REL_Y
    
    if INTERACT["pan_active"]:
        # Przesuwaj tło (Pan)
        dx = e.x - INTERACT["pan_sx"]
        dy = e.y - INTERACT["pan_sy"]
        PAN_X += dx
        PAN_Y += dy
        INTERACT["pan_sx"], INTERACT["pan_sy"] = e.x, e.y
        render_view()
    elif INTERACT["drag"]:
        # Przesuwaj logo
        dx = e.x - INTERACT["sx"]
        dy = e.y - INTERACT["sy"]
        canv.move(INTERACT["drag"], dx, dy)
        INTERACT["sx"], INTERACT["sy"] = e.x, e.y

def on_lpm_up(e):
    """Obsługa puszczenia LPM: aktualizacja pozycji względnej logo"""
    global REL_X, REL_Y
    
    if INTERACT["pan_active"]:
        INTERACT["pan_active"] = False
    elif INTERACT["drag"] and CACHE_BG:
        # Aktualizuj REL_X/Y z uwzględnieniem offsetu Pan
        coords = canv.coords(INTERACT["drag"])
        cw, ch = canv.winfo_width(), canv.winfo_height()
        bw, bh = CACHE_BG.width, CACHE_BG.height
        ox = (cw - bw) // 2 + PAN_X
        oy = (ch - bh) // 2 + PAN_Y
        REL_X = (coords[0] - ox) / bw if bw > 0 else 0.5
        REL_Y = (coords[1] - oy) / bh if bh > 0 else 0.5
        INTERACT["drag"] = None

# Rotacja środkowym przyciskiem
def on_mpm_down(e):
    INTERACT["ax"] = e.x
    INTERACT["start_a"] = var_rot.get()

def on_mpm_motion(e):
    var_rot.set((INTERACT["start_a"] + (e.x - INTERACT["ax"]) // 2) % 360)
    render_view()

canv.bind("<Button-1>", on_lpm_down)
canv.bind("<B1-Motion>", on_lpm_motion)
canv.bind("<ButtonRelease-1>", on_lpm_up)
canv.bind("<Button-2>", on_mpm_down)
canv.bind("<B2-Motion>", on_mpm_motion)
canv.bind("<Control-MouseWheel>", on_scr)
canv.bind("<Configure>", lambda e: render_view())

# DRAG & DROP OS HOOK
windnd.hook_dropfiles(root, func=on_os_drop)

root.mainloop()