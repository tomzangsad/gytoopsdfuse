import os
import json
import shutil
import glob
from jproperties import Properties


# ===========================================
# 🔍 หาโฟลเดอร์ IA overlay version แบบอัตโนมัติ
# ===========================================
def find_ia_overlay_folder():
    root = "pack"
    for f in os.listdir(root):
        if f.startswith("ia_overlay") and os.path.isdir(os.path.join(root, f)):
            return os.path.join(root, f)
    return None


IA_OVERLAY = find_ia_overlay_folder()
if IA_OVERLAY:
    print(f"🟦 Detected IA Overlay Folder: {IA_OVERLAY}")
else:
    print("⚠️ No IA overlay folder found!")


# ===========================================
# 🔧 อัปเดต item_texture.json
# ===========================================
def update_item_texture_json(gmdl_id, atlas_path):
    item_texture_file = "staging/target/rp/textures/item_texture.json"

    if not os.path.exists(item_texture_file):
        print("⚠️ item_texture.json not found, skipping update.")
        return

    with open(item_texture_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    tex = data.get("texture_data", {})
    tex[gmdl_id] = {"textures": atlas_path}

    data["texture_data"] = tex

    with open(item_texture_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"🔧 Updated item_texture.json: {gmdl_id} → {atlas_path}")


# ===========================================
# 🔧 ล้าง override
# ===========================================
def process_json_file(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return []

    with open(file_path, "r") as f:
        data = json.load(f)

    overrides = data.get("overrides", [])
    processed_overrides = []
    seen_custom_model_data = set()

    for override in overrides:
        predicate = override.get("predicate", {})
        model = override.get("model", "")

        if "trim_type" in predicate:
            continue

        cmd = predicate.get("custom_model_data")
        if cmd is not None:
            if cmd in seen_custom_model_data:
                continue
            seen_custom_model_data.add(cmd)

        processed_overrides.append(override)

    data["overrides"] = processed_overrides
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Cleaned {file_path}")
    return processed_overrides


# ===========================================
# 🔧 ล้าง duplicate armor entries
# ===========================================
def remove_duplicates_with_custom_model_data(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        armor_types = [
            "minecraft:leather_helmet", "minecraft:leather_chestplate",
            "minecraft:leather_leggings", "minecraft:leather_boots",
            "minecraft:iron_helmet", "minecraft:iron_chestplate",
            "minecraft:iron_leggings", "minecraft:iron_boots",
            "minecraft:diamond_helmet", "minecraft:diamond_chestplate",
            "minecraft:diamond_leggings", "minecraft:diamond_boots",
            "minecraft:netherite_helmet", "minecraft:netherite_chestplate",
            "minecraft:netherite_leggings", "minecraft:netherite_boots"
        ]

        for armor in armor_types:
            if armor not in data:
                continue

            unique = {}
            for entry in data[armor]:
                cmd = entry.get("custom_model_data")
                if cmd not in unique:
                    unique[cmd] = entry

            data[armor] = list(unique.values())

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        print(f"🧩 Cleaned duplicates in {file_path}")
    except:
        pass


# ===========================================
# 🔥 อ่าน IA model (1.21+)
# ===========================================
def process_ia_overlay_model(namespace, item, i):
    if not IA_OVERLAY:
        return None

    model_path = f"{IA_OVERLAY}/assets/{namespace}/models/equipment/{item}.json"
    if not os.path.exists(model_path):
        return None

    print(f"🟦 IA model detected: {model_path}")

    with open(model_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tex = data.get("texture")
    if not tex:
        print(f"⚠️ No texture in IA model: {model_path}")
        return None

    if ":" in tex:
        tex = tex.split(":")[1]

    layer_folder = "humanoid_leggings" if i == 2 else "humanoid"

    src = f"{IA_OVERLAY}/assets/{namespace}/textures/entity/equipment/{layer_folder}/{item}.png"
    dest = f"staging/target/rp/textures/armor_layer/{item}.png"

    os.makedirs(os.path.dirname(dest), exist_ok=True)

    if os.path.exists(src):
        shutil.copy(src, dest)
        print(f"🟦 Copied IA armor texture → {dest}")
        return item
    else:
        print(f"⚠️ Missing IA armor texture: {src}")
        return None


# ===========================================
# 🧱 Generate attachable
# ===========================================
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


# ===========================================
# 🚀 MAIN
# ===========================================
geyser_map = "staging/target/geyser_mappings.json"
if os.path.exists(geyser_map):
    remove_duplicates_with_custom_model_data(geyser_map)

optifine = Properties()
items = ["leather_helmet", "leather_chestplate", "leather_leggings", "leather_boots"]

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

            # ==========================
            # 🔥 1) ลองใช้ IA overlay (ใหม่)
            # ==========================
            layer = process_ia_overlay_model(namespace, item, i)

            # ==========================
            # 🔥 2) ถ้าไม่มี → ใช้ CIT เดิม
            # ==========================
            if not layer:
                prop_file = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{namespace}_{item}.properties"
                if not os.path.exists(prop_file):
                    print(f"⚠️ Missing {prop_file}")
                    continue

                optifine.load(open(prop_file, "rb"))

                layer_key = f"texture.leather_layer_{2 if i == 2 else 1}"

                if optifine.get(layer_key):
                    layer = optifine.get(layer_key).data.split(".")[0]
                elif optifine.get(f"{layer_key}_overlay"):
                    layer = optifine.get(f"{layer_key}_overlay").data.split(".")[0]
                else:
                    print(f"⚠️ No layer info in {prop_file}")
                    continue

                src_tex = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{layer}.png"
                dst_tex = f"staging/target/rp/textures/armor_layer/{layer}.png"

                if os.path.exists(src_tex):
                    shutil.copy(src_tex, dst_tex)
                    print(f"🟩 Copied CIT texture → {dst_tex}")
                else:
                    print(f"⚠️ Missing CIT texture: {src_tex}")

            # ==========================
            # Copy 2D Icon (เหมือนเดิม)
            # ==========================
            model_json_path = f"pack/assets/{namespace}/models/{path}.json"

            if not os.path.exists(model_json_path):
                print(f"⚠️ Missing model file: {model_json_path}")
                continue

            with open(model_json_path, "r") as f:
                model_data = json.load(f)

            textures = model_data.get("textures", {})
            icon_texture = textures.get("layer0") or textures.get("layer1")

            if ":" in icon_texture:
                icon_texture = icon_texture.split(":")[1]

            src_icon = f"pack/assets/{namespace}/textures/{icon_texture}.png"
            dest_icon = f"staging/target/rp/textures/{namespace}/{icon_texture}.png"

            os.makedirs(os.path.dirname(dest_icon), exist_ok=True)

            if os.path.exists(src_icon):
                shutil.copy(src_icon, dest_icon)
                print(f"🖼️ Copied icon → {dest_icon}")
            else:
                print(f"⚠️ Missing icon texture: {src_icon}")
                continue

            # ==========================
            # หา gmdl จาก attachable
            # ==========================
            afile = glob.glob(f"staging/target/rp/attachables/{namespace}/{path}*.json")
            if not afile:
                print(f"⚠️ No attachable found for {model}")
                continue

            with open(afile[0], "r") as f:
                da = json.load(f)["minecraft:attachable"]
                gmdl = da["description"]["identifier"].split(":")[1]

            # ==========================
            # Add icon → icons.csv
            # ==========================
            atlas = f"textures/{namespace}/{icon_texture}.png"

            os.makedirs("scratch_files", exist_ok=True)
            with open("scratch_files/icons.csv", "a", encoding="utf-8") as f:
                f.write(f"{gmdl},{atlas}\n")

            print(f"📌 Added icon atlas: {gmdl} → {atlas}")

            # ==========================
            # Update item_texture.json
            # ==========================
            update_item_texture_json(gmdl, atlas)

            # ==========================
            # Generate Bedrock armor
            # ==========================
            pfile = afile[0].replace(".json", ".player.json")
            write_armor(pfile, gmdl, layer, i)

        except Exception as e:
            print(f"❌ Error while processing {model}: {e}")
            continue
