from PIL import Image
from font_sprite import sprite
import glob, os, json

# ==================================================
# CONFIG
# ==================================================
lines = [0,1,2,3,4,5,6,7,8,9,"a","b","c","d","e","f"]

FONT_JSON_PATHS = [
    "pack/assets/minecraft/font/default.json",
    "pack/assets/nexo/font/default.json"
]

# ==================================================
# LOAD FONT PROVIDERS
# ==================================================
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
        print("[FONT ERROR]", font_path, e)

# ==================================================
# PARSE PROVIDERS (SAFE)
# ==================================================
symbols = []
paths = []
heights = []
ascents = []

for d in data["providers"]:
    try:
        chars = d.get("chars")
        if not chars:
            continue

        symbol = "".join(chars)

        # ❗ ข้าม multi-char / emoji
        if len(symbol) != 1:
            print(f"[SKIP SYMBOL] multi-char: {repr(symbol)}")
            continue

        ord(symbol)  # validate

        symbols.append(chars)
        paths.append(d["file"])
        heights.append(d.get("height", 8))
        ascents.append(d.get("ascent", 7))

    except Exception as e:
        print("[SKIP SYMBOL ERROR]", e)
        continue

# ==================================================
# CREATE GLYPH LIST (SAFE)
# ==================================================
glyphs = []

for chars in symbols:
    try:
        symbol = "".join(chars)
        if len(symbol) != 1:
            continue

        code = f"{ord(symbol):04X}"
        glyphs.append(code[:2])

    except Exception as e:
        print("[GLYPH SKIP]", e)
        continue

glyphs = sorted(set(glyphs))
print("[FONT FILE]")
print(glyphs)

# ==================================================
# UTILS
# ==================================================
def createfolder(glyph):
    os.makedirs(f"images/{glyph}", exist_ok=True)
    os.makedirs(f"export/{glyph}", exist_ok=True)
    os.makedirs("font", exist_ok=True)

def create_empty(glyph, blankimg):
    for a in lines:
        for b in lines:
            name = f"{a}{b}"
            path = f"images/{glyph}/0x{glyph}{name}.png"
            if os.path.isfile(path):
                continue
            Image.open(blankimg).copy().save(path, "PNG")

def imagetoexport(glyph, blankimg):
    for img in os.listdir(f"images/{glyph}"):
        if not img.endswith(".png"):
            continue

        base = Image.open(blankimg)
        logo = Image.open(f"images/{glyph}/{img}")

        bw, bh = base.size
        lw, lh = logo.size

        if lw > bw//2 and lh > bh//2:
            pos = (0,0)
        else:
            pos = (0, (bh//2)-(lh//2))

        base.paste(logo, pos)
        base.save(f"export/{glyph}/{img}")

# ==================================================
# MAIN CONVERTER
# ==================================================
listglyphdone = []

def converterpack(glyph):
    try:
        if glyph in listglyphdone:
            return

        createfolder(glyph)
        maxw = maxh = 0

        for chars, path in zip(symbols, paths):
            symbol = "".join(chars)
            code = f"{ord(symbol):04X}"
            if code[:2] != glyph:
                continue

            imgname = f"0x{glyph}{code[2:]}.png"

            try:
                if ":" in path:
                    ns, p = path.split(":", 1)
                    img = Image.open(f"pack/assets/{ns}/textures/{p}")
                else:
                    img = Image.open(f"pack/assets/minecraft/textures/{path}")

                img.save(f"images/{glyph}/{imgname}", "PNG")

                w,h = img.size
                maxw, maxh = max(maxw,w), max(maxh,h)

            except Exception as e:
                print("[IMAGE SKIP]", e)
                continue

        if maxw == 0 or maxh == 0:
            print(f"[GLYPH EMPTY] {glyph}")
            return

        size = max(maxw, maxh) + 1
        Image.open("blank256.png").resize((size,size)).save("blankimg.png")

        create_empty(glyph, "blankimg.png")
        imagetoexport(glyph, "blankimg.png")
        sprite(glyph, size*16, (size,size))

        listglyphdone.append(glyph)
        print(f"[GLYPH DONE] {glyph}")

    except Exception as e:
        print(f"[GLYPH FAIL] {glyph} : {e}")

# ==================================================
# RUN
# ==================================================
for glyph in glyphs:
    converterpack(glyph)
