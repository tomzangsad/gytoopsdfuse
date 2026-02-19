from PIL import Image
from font_sprite import sprite
from io import BytesIO
import glob, os, json

lines = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "a", "b", "c", "d", "e", "f"]
FONT_JSON_PATHS = [
    "pack/assets/minecraft/font/default.json",
    "pack/assets/nexo/font/default.json"
]

data = {"providers": []}

for font_path in FONT_JSON_PATHS:
    if not os.path.isfile(font_path):
        print(f"[FONT] Skip (not found): {font_path}")
        continue

    try:
        with open(font_path, "r", encoding="utf-8") as f:
            font_data = json.load(f)

        providers = font_data.get("providers", [])
        data["providers"].extend(providers)

        print(f"[FONT] Loaded: {font_path} ({len(providers)} providers)")

    except Exception as e:
        print("[FONT ERROR]", font_path)
        print(e)

symbols = []
paths = []
heights = []
ascents = []
for d in data['providers']:
    try:
        chars = d['chars']
        # ตรวจสอบว่า chars มีแค่ 1 unicode character เท่านั้น
        symbolbe = ''.join(chars)
        if len(symbolbe) != 1:
            print(f"[FONT SKIP] chars has {len(symbolbe)} characters (need exactly 1): {repr(symbolbe)} - file: {d.get('file', 'unknown')}")
            continue
        symbols.append(chars)
        paths.append(d['file'])
        heights.append(d['height'])
        ascents.append(d['ascent'])
    except:
        continue

def createfolder(glyph):
    os.makedirs(f"images/{glyph}", exist_ok = True)
    os.makedirs(f"export/{glyph}", exist_ok = True)
    os.makedirs(f"font/", exist_ok = True)
    
def create_empty(glyph, blankimg):
    for line in lines:
        for linee in lines:
            if linee != lines:
                name = f"{line}{linee}"
                if os.path.isfile(f"images/{glyph}/0x{glyph}{name}.png"):
                    continue
                else:
                    imagesus = Image.open(blankimg)
                    image = imagesus.copy()
                    image.save(f"images/{glyph}/0x{glyph}{name}.png", "PNG")
    for line in lines:
        name = f"{line}{line}"
        if os.path.isfile(f"images/{glyph}/0x{glyph}{name}.png"):
            continue
        else:
            imagesus = Image.open(blankimg)
            image = imagesus.copy()
            image.save(f"images/{glyph}/0x{glyph}{name}.png", "PNG")

def imagetoexport(glyph, blankimg):
    filelist = [file for file in os.listdir(f'images/{glyph}') if file.endswith('.png')]
    for img in filelist:
        image = Image.open(blankimg)
        logo = Image.open(f'images/{glyph}/{img}')
        image_copy = image.copy()
        w, h = image.size
        wl, hl = logo.size
        for height, symboll in zip(heights, symbols):
            symbolbe = ''.join(symboll)
            # ข้าม chars ที่มีมากกว่า 1 unicode
            if len(symbolbe) != 1:
                continue
            val = ord(symbolbe)
            hex_str = f"{val:04X}"
            symbol = hex_str[-2:]
            
            # Legacy logic support if needed, or just use robust calculation
            # For 0xABCD -> symbol=CD
            # For 0x101 -> 0101 -> symbol=01
            # For 0x41 -> 0041 -> symbol=41
            name = f"0x{glyph}{symbol}"
            imgname = f"0x{glyph}{img}"
            if name == imgname:
                if height >= 1 and height < w and height < h:
                    size = (height, height)
                    logo.thumbnail(size,Image.ANTIALIAS)                 
        if wl > (w/2) and hl > (h/2):
            position = (0, 0)
            image_copy.paste(logo, position)
            image_copy.save(f"export/{glyph}/{img}")
        else:
            position = (0, (h//2) - (hl//2))
            image_copy.paste(logo, position)
            image_copy.save(f"export/{glyph}/{img}")

            
glyphs = []
for i in symbols:
    if i not in glyphs:
        try:
            symbolbe = ''.join(i)
            # ข้าม chars ที่มีมากกว่า 1 unicode
            if len(symbolbe) != 1:
                print(f"[GLYPH SKIP] chars has {len(symbolbe)} characters: {repr(symbolbe)}")
                continue
            val = ord(symbolbe)
            hex_str = f"{val:04X}"
            ab = hex_str[:-2]
            glyphs.append(ab.upper())
        except:
            print(f"Symbol Error: {symbolbe}")
            symbols.remove(i)
            continue
glyphs = list(dict.fromkeys(glyphs))
print("[FONT FILE]")
print(glyphs)

listglyphdone = []
def converterpack(glyph):
    createfolder(glyph)
    if len(symbols) == len(paths):
        maxsw, maxsh = 0, 0
        for symboll, path in zip(symbols, paths):
            symbolbe = ''.join(symboll)
            val = ord(symbolbe)
            hex_str = f"{val:04X}"
            symbol = hex_str[-2:]
            symbolcheck = hex_str[:-2]
            
            if symbolcheck.upper() not in glyphs:
                 glyphs.append(symbolcheck.upper())
            if (symbolcheck.upper()) == (glyph.upper()):
                if ":" in path:
                    try:
                        namespace = path.split(":")[0]
                        pathnew = path.split(":")[1]
                        imagefont = Image.open(f"pack/assets/{namespace}/textures/{pathnew}")
                        image = imagefont.copy()
                        image.save(f"images/{glyph}/0x{glyph}{symbol}.png", "PNG")
                    except Exception as e:
                        print(e)
                        continue
                else:
                    try:
                        imagefont = Image.open(f"pack/assets/minecraft/textures/{path}")
                        image = imagefont.copy()
                        image.save(f"images/{glyph}/0x{glyph}{symbol}.png", "PNG")
                    except Exception as e: 
                        print(e)
                        continue
            else:
                continue
        else:                
            files = glob.glob(f"images/{glyph}/*.png")
            for file in files:
                image = Image.open(file)
                sw, sh = image.size
                maxsw, maxsh = (max(maxsw, sw), max(maxsh, sh))
            if maxsw == maxsh:
                size = (int(maxsw + 1), int(maxsw + 1))
            elif maxsw > maxsh:
                size = (int(maxsw + 1), int(maxsw + 1))
            elif maxsh > maxsw:
                size = (int(maxsh + 1), int(maxsh + 1))
            if size == (0, 0):
                pass
            else:
                glyphsize = size * 16
                img = Image.open("blank256.png")
                imgre = img.resize(size)
                imgre.save("blankimg.png")
                blankimg = "blankimg.png"
                create_empty(glyph, blankimg) 
                imagetoexport(glyph, blankimg)
                sprite(glyph, glyphsize, size)
                listglyphdone.append(glyph)
            
for glyph in glyphs:
    converterpack(glyph)
