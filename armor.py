import os
import json
import shutil
import glob
from jproperties import Properties

# =====================================================
# 🔵 หา overlay หลายเวอร์ชัน (รองรับหลายโฟลเดอร์)
# =====================================================
def find_all_ia_overlays():
    root = "pack"
    overlays = []
    for f in os.listdir(root):
        if f.startswith("ia_overlay") and os.path.isdir(os.path.join(root, f)):
            overlays.append(os.path.join(root, f))
    return overlays

IA_OVERLAYS = find_all_ia_overlays()
print("🟦 IA Overlays detected:", IA_OVERLAYS)


# =====================================================
# 📘 หา model.json จาก overlay ใดก็ได้
# =====================================================
def find_model_in_overlays(namespace, item):
    for ov in IA_OVERLAYS:
        model_path = f"{ov}/assets/{namespace}/models/equipment/{item}.json"
        if os.path.exists(model_path):
            print(f"🟩 Model found in: {model_path}")
            return model_path
    return None


# =====================================================
# 📘 หา texture ใน overlay ทั้งหมด
# =====================================================
def find_texture_in_overlays(namespace, item, i):
    layer_folder = "humanoid_leggings" if i == 2 else "humanoid"

    for ov in IA_OVERLAYS:
        tex_path = f"{ov}/assets/{namespace}/textures/entity/equipment/{layer_folder}/{item}.png"
        if os.path.exists(tex_path):
            print(f"🟩 Texture found in: {tex_path}")
            return tex_path

    print(f"❌ Texture not found in ANY overlay for {item}")
    return None


# =====================================================
# 📘 ใช้ overlay (model+texture) ถ้ามี
# =====================================================
def process_ia_overlay(namespace, item, i):
    model_path = find_model_in_overlays(namespace, item)
    if not model_path:
        return None

    with open(model_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tex = data.get("texture")
    if not tex:
        return None

    if ":" in tex:
        tex = tex.split(":")[1]

    # หา texture จริง
    src = find_texture_in_overlays(namespace, item, i)
    if not src:
        return None

    dest = f"staging/target/rp/textures/armor_layer/{item}.png"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy(src, dest)

    print(f"🟦 Copied IA armor texture → {dest}")
    return item   # layer name = item name


# =====================================================
# 🔧 อัปเดต item_texture.json
# =====================================================
def update_item_texture_json(gmdl_id, atlas_path):
    item_texture_file = "staging/target/rp/textures/item_texture.json"

    if not os.path.exists(item_texture_file):
        print("⚠️ item_texture.json not found, skipping.")
        return

    with open(item_texture_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    tex = data.get("texture_data", {})
    tex[gmdl_id] = {"textures": atlas_path}

    data["texture_data"] = tex

    with open(item_texture_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"🔧 Updated item_texture.json: {gmdl_id} → {atlas_path}")


# =====================================================
# 🔧 ล้าง overrides (remove duplicated custom_model_data)
# =====================================================
def process_json_file(file_path):
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r") as f:
        data = json.load(f)

    overrides = data.get("overrides", [])
    processed = []
    seen = set()

    for o in overrides:
        pred = o.get("predicate", {})

        # skip trims
        if "trim_type" in pred:
            continue

        cmd = pred.get("custom_model_data")
        if cmd is not None:
            if cmd in seen:
                continue
            seen.add(cmd)

        processed.append(o)

    data["overrides"] = processed

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    return processed


# =====================================================
# 🧱 Generate attachable (.player.json)
# =====================================================
def write_armor(file, gmdl, layer, i):
    type_map = ["helmet", "chestplate", "leggings", "boots"]
    armor_type = type_map[i]

    ajson = {
        "format_version": "1.10.0",
        "minecraft:attachable": {
            "description": {
                "identifier": f"geyser_custom:{gmdl}.player",
                "item": {f"geyser_custom:{gmdl}": "query.owner_identifier == 'minecraft:player'"},
                "materials": {
                    "default": "armor_leather",
                    "enchanted": "armor_leather_enchanted",
                },
                "textures": {
                    "default": f"textures/armor_layer/{layer}",
                    "enchanted": "textures/misc/enchanted_item_glint",
                },
                "geometry": {"default": f"geometry.player.armor.{armor_type}"},
                "scripts": {"parent_setup": "variable.helmet_layer_visible = 0.0;"},
                "render_controllers": ["controller.render.armor"],
            },
        },
    }

    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "w") as f:
        json.dump(ajson, f, indent=4)

    print(f"✅ Generated {file}")


# =====================================================
# 🚀 MAIN
# =====================================================
optifine = Properties()
items = ["leather_helmet", "leather_chestplate", "leather_leggings", "leather_boots",
        "netherite_helmet", "netherite_chestplate", "netherite_leggings", "netherite_boots"]

for i, armor in enumerate(items):

    item_json = f"pack/assets/minecraft/models/item/{armor}.json"
    overrides = process_json_file(item_json)

    for o in overrides:
        model = o.get("model")
        if not model:
            continue

        try:
            namespace, path = model.split(":")
            item = path.split("/")[-1]

            # ==========================================
            # 1) TRY IA OVERLAY (new IA armor)
            # ==========================================
            layer = process_ia_overlay(namespace, item, i)

            # ==========================================
            # 2) FALLBACK → CIT (old armor)
            # ==========================================
            if not layer:
                prop_file = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{namespace}_{item}.properties"

                if not os.path.exists(prop_file):
                    print(f"⚠️ Missing {prop_file}")
                    continue

                optifine.load(open(prop_file, "rb"))
                layer_key = f"texture.leather_layer_{2 if i == 2 else 1}"

                if optifine.get(layer_key):
                    layer = optifine.get(layer_key).data.split(".")[0]
                else:
                    continue

                texture_src = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{layer}.png"
                os.makedirs("staging/target/rp/textures/armor_layer", exist_ok=True)

                shutil.copy(texture_src, f"staging/target/rp/textures/armor_layer/{layer}.png")
                print(f"🟩 Copied CIT armor → {layer}.png")

            # ==========================================
            # Copy ICON
            # ==========================================
            model_json_path = f"pack/assets/{namespace}/models/{path}.json"

            if not os.path.exists(model_json_path):
                print("⚠️ Missing icon model:", model_json_path)
                continue

            with open(model_json_path, "r") as f:
                md = json.load(f)

            textures = md.get("textures", {})
            icon_texture = textures.get("layer0") or textures.get("layer1")

            if ":" in icon_texture:
                icon_texture = icon_texture.split(":")[1]

            src = f"pack/assets/{namespace}/textures/{icon_texture}.png"
            dst = f"staging/target/rp/textures/{namespace}/{icon_texture}.png"
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
            print(f"🖼️ Copied icon → {dst}")

            # ==========================================
            # Load attachable to get gmdl
            # ==========================================
            afile = glob.glob(f"staging/target/rp/attachables/{namespace}/{path}*.json")
            if not afile:
                print("⚠️ No attachable for:", model)
                continue

            with open(afile[0], "r") as f:
                da = json.load(f)["minecraft:attachable"]
                gmdl = da["description"]["identifier"].split(":")[1]

            # ==========================================
            # Add icon to icons.csv
            # ==========================================
            atlas = f"textures/{namespace}/{icon_texture}.png"
            os.makedirs("scratch_files", exist_ok=True)
            with open("scratch_files/icons.csv", "a") as f:
                f.write(f"{gmdl},{atlas}\n")

            print(f"📌 Icon added: {gmdl} → {atlas}")

            # ==========================================
            # Update item_texture.json
            # ==========================================
            update_item_texture_json(gmdl, atlas)

            # ==========================================
            # Generate .player.json
            # ==========================================
            pfile = afile[0].replace(".json", ".player.json")
            write_armor(pfile, gmdl, layer, i)

        except Exception as e:
            print("❌ Error:", e)
            continue
