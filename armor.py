
# import os
# import json
# import shutil
# import glob
# from jproperties import Properties

# # ===============================
# # 🔧 อัปเดต item_texture.json
# # ===============================
# def update_item_texture_json(gmdl_id, atlas_path):
#     """อัปเดต path ของไอเท็มใน item_texture.json ให้ตรงกับไฟล์ที่ Python วาง"""
#     item_texture_file = "staging/target/rp/textures/item_texture.json"

#     if not os.path.exists(item_texture_file):
#         print("⚠️ item_texture.json not found, skipping update.")
#         return

#     with open(item_texture_file, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     tex = data.get("texture_data", {})
#     tex[gmdl_id] = {"textures": atlas_path}   # ⭐ แก้ path ตรงนี้

#     data["texture_data"] = tex

#     with open(item_texture_file, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=4)

#     print(f"🔧 Updated item_texture.json: {gmdl_id} → {atlas_path}")


# # ===============================
# # 🔧 ฟังก์ชันล้าง override
# # ===============================
# def process_json_file(file_path):
#     if not os.path.exists(file_path):
#         print(f"❌ File not found: {file_path}")
#         return []

#     with open(file_path, "r") as f:
#         data = json.load(f)

#     overrides = data.get("overrides", [])
#     processed_overrides = []
#     seen_custom_model_data = set()

#     for override in overrides:
#         predicate = override.get("predicate", {})
#         model = override.get("model", "")

#         if "trim_type" in predicate:
#             continue

#         cmd = predicate.get("custom_model_data")
#         if cmd is not None:
#             if cmd in seen_custom_model_data:
#                 continue
#             seen_custom_model_data.add(cmd)

#         processed_overrides.append(override)

#     data["overrides"] = processed_overrides
#     with open(file_path, "w") as f:
#         json.dump(data, f, indent=4)

#     print(f"✅ Cleaned {file_path}")
#     return processed_overrides


# def remove_duplicates_with_custom_model_data(file_path):
#     try:
#         with open(file_path, "r") as f:
#             data = json.load(f)

#         item_types = [
#             "minecraft:leather_helmet",
#             "minecraft:leather_chestplate",
#             "minecraft:leather_leggings",
#             "minecraft:leather_boots",
#         ]

#         for item_type in item_types:
#             if item_type not in data:
#                 continue

#             unique_entries = {}
#             for entry in data[item_type]:
#                 cmd = entry.get("custom_model_data")
#                 if cmd not in unique_entries:
#                     unique_entries[cmd] = entry

#             data[item_type] = list(unique_entries.values())

#         with open(file_path, "w") as f:
#             json.dump(data, f, indent=4)
#         print(f"🧩 Cleaned duplicates in {file_path}")
#     except:
#         pass


# def write_armor(file, gmdl, layer, i):
#     type_map = ["helmet", "chestplate", "leggings", "boots"]
#     armor_type = type_map[i]

#     ajson = {
#         "format_version": "1.10.0",
#         "minecraft:attachable": {
#             "description": {
#                 "identifier": f"geyser_custom:{gmdl}.player",
#                 "item": {f"geyser_custom:{gmdl}": "query.owner_identifier == 'minecraft:player'"},
#                 "materials": {
#                     "default": "armor_leather",
#                     "enchanted": "armor_leather_enchanted",
#                 },
#                 "textures": {
#                     "default": f"textures/armor_layer/{layer}",
#                     "enchanted": "textures/misc/enchanted_item_glint",
#                 },
#                 "geometry": {"default": f"geometry.player.armor.{armor_type}"},
#                 "scripts": {"parent_setup": "variable.helmet_layer_visible = 0.0;"},
#                 "render_controllers": ["controller.render.armor"],
#             },
#         },
#     }

#     os.makedirs(os.path.dirname(file), exist_ok=True)
#     with open(file, "w") as f:
#         json.dump(ajson, f, indent=4)

#     print(f"✅ Generated {file}")


# # ===============================
# # 🚀 MAIN START
# # ===============================
# geyser_mappings_file = "staging/target/geyser_mappings.json"
# if os.path.exists(geyser_mappings_file):
#     remove_duplicates_with_custom_model_data(geyser_mappings_file)

# optifine = Properties()
# item_type = ["leather_helmet", "leather_chestplate", "leather_leggings", "leather_boots"]

# for i, armor in enumerate(item_type):

#     item_json = f"pack/assets/minecraft/models/item/{armor}.json"
#     overrides = process_json_file(item_json)

#     for override in overrides:
#         model = override.get("model")
#         if not model:
#             continue

#         try:
#             namespace, path = model.split(":")
#             item = path.split("/")[-1]

#             # ==========================
#             # โหลด .properties
#             # ==========================
#             prop_file = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{namespace}_{item}.properties"
#             if not os.path.exists(prop_file):
#                 print(f"⚠️ Missing {prop_file}")
#                 continue

#             optifine.load(open(prop_file, "rb"))

#             layer_key = f"texture.leather_layer_{2 if i == 2 else 1}"
#             layer = None

#             if optifine.get(layer_key):
#                 layer = optifine.get(layer_key).data.split(".")[0]
#             elif optifine.get(f"{layer_key}_overlay"):
#                 layer = optifine.get(f"{layer_key}_overlay").data.split(".")[0]
#             else:
#                 print(f"⚠️ No layer info found in {prop_file}")
#                 continue

#             # ==========================
#             # Copy armor texture
#             # ==========================
#             os.makedirs("staging/target/rp/textures/armor_layer", exist_ok=True)
#             src_texture = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{layer}.png"

#             if os.path.exists(src_texture):
#                 shutil.copy(src_texture, f"staging/target/rp/textures/armor_layer/{layer}.png")
#                 print(f"🧩 Copied {layer}.png → armor_layer/")
#             else:
#                 print(f"⚠️ Missing armor texture: {src_texture}")

#             # ==========================
#             # Copy 2D icon
#             # ==========================
#             model_json_path = f"pack/assets/{namespace}/models/{path}.json"

#             if not os.path.exists(model_json_path):
#                 print(f"⚠️ Missing model file: {model_json_path}")
#                 continue

#             with open(model_json_path, "r") as f:
#                 model_data = json.load(f)

#             textures = model_data.get("textures", {})
#             icon_texture = textures.get("layer0") or textures.get("layer1")

#             if icon_texture == "item/empty" and textures.get("layer1"):
#                 icon_texture = textures["layer1"]

#             if ":" in icon_texture:
#                 icon_texture = icon_texture.split(":")[1]

#             src_icon = f"pack/assets/{namespace}/textures/{icon_texture}.png"
#             dest_icon = f"staging/target/rp/textures/{namespace}/{icon_texture}.png"

#             os.makedirs(os.path.dirname(dest_icon), exist_ok=True)

#             if os.path.exists(src_icon):
#                 shutil.copy(src_icon, dest_icon)
#                 print(f"🖼️ Copied item icon → {dest_icon}")
#             else:
#                 print(f"⚠️ Missing icon texture: {src_icon}")
#                 continue

#             # ==========================
#             # หา gmdl จาก attachable
#             # ==========================
#             afile = glob.glob(f"staging/target/rp/attachables/{namespace}/{path}*.json")
#             if not afile:
#                 print(f"⚠️ No attachable found for {model}")
#                 continue

#             with open(afile[0], "r") as f:
#                 da = json.load(f)["minecraft:attachable"]
#                 gmdl = da["description"]["identifier"].split(":")[1]

#             # ==========================
#             # Add icon → icons.csv
#             # ==========================
#             atlas_texture_path = f"textures/{namespace}/{icon_texture}.png"

#             icons_csv = "scratch_files/icons.csv"
#             os.makedirs("scratch_files", exist_ok=True)

#             with open(icons_csv, "a", encoding="utf-8") as f:
#                 f.write(f"{gmdl},{atlas_texture_path}\n")

#             print(f"📌 Added icon to atlas: {gmdl} → {atlas_texture_path}")

#             # ==========================
#             # ⭐ อัปเดต item_texture.json
#             # ==========================
#             update_item_texture_json(gmdl, atlas_texture_path)

#             # ==========================
#             # Generate player attachable
#             # ==========================
#             pfile = afile[0].replace(".json", ".player.json")
#             write_armor(pfile, gmdl, layer, i)

#         except Exception as e:
#             print(f"❌ Error while processing {model}: {e}")
#             continue



import os
import json
import shutil
import glob
from jproperties import Properties
from collections import defaultdict

# ===============================
# 🔧 อัปเดต item_texture.json
# ===============================
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


# ===============================
# 🔧 ล้าง override ซ้ำ
# ===============================
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


def remove_duplicates_with_custom_model_data(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        item_type = [
            # Leather
            "leather_helmet", "leather_chestplate", "leather_leggings", "leather_boots",
            # Chainmail
            "chainmail_helmet", "chainmail_chestplate", "chainmail_leggings", "chainmail_boots",
            # Iron
            "iron_helmet", "iron_chestplate", "iron_leggings", "iron_boots",
            # Gold
            "golden_helmet", "golden_chestplate", "golden_leggings", "golden_boots",
            # Diamond
            "diamond_helmet", "diamond_chestplate", "diamond_leggings", "diamond_boots",
            # Netherite
            "netherite_helmet", "netherite_chestplate", "netherite_leggings", "netherite_boots"
        ]


        for item_type in item_types:
            if item_type not in data:
                continue

            unique_entries = {}
            for entry in data[item_type]:
                cmd = entry.get("custom_model_data")
                if cmd not in unique_entries:
                    unique_entries[cmd] = entry

            data[item_type] = list(unique_entries.values())

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"🧩 Cleaned duplicates in {file_path}")
    except:
        pass


def write_armor(file, gmdl, layer, i):
    type_map = ["helmet", "chestplate", "leggings", "boots"]
    armor_type = type_map[i]

    # 🧩 ดึงวัสดุจากชื่อ เช่น leather / chainmail / iron / golden / diamond / netherite
    material = gmdl.split("_")[0]
    if material == "golden":
        material = "gold"

    ajson = {
        "format_version": "1.10.0",
        "minecraft:attachable": {
            "description": {
                "identifier": f"geyser_custom:{gmdl}.player",
                "item": {f"geyser_custom:{gmdl}": "query.owner_identifier == 'minecraft:player'"},
                "materials": {
                    "default": f"armor_{material}",
                    "enchanted": f"armor_{material}_enchanted",
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



# ===============================
# 🧭 Fallback: Scan armor layers
# ===============================
def find_armor_layers(base_path):
    armor_sets = defaultdict(lambda: {"layer_1": None, "layer_2": None})
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith("_layer_1.png") or file.endswith("_layer_2.png"):
                key = file.replace("_layer_1.png", "").replace("_layer_2.png", "")
                full = os.path.join(root, file)
                if file.endswith("_layer_1.png"):
                    armor_sets[key]["layer_1"] = full
                else:
                    armor_sets[key]["layer_2"] = full
    return armor_sets


# ===============================
# 🚀 MAIN START
# ===============================
geyser_mappings_file = "staging/target/geyser_mappings.json"
if os.path.exists(geyser_mappings_file):
    remove_duplicates_with_custom_model_data(geyser_mappings_file)

optifine = Properties()
item_type = ["leather_helmet", "leather_chestplate", "leather_leggings", "leather_boots"]

PACK_PATH = r"C:\Users\ToMZanG\Downloads\pack"

armor_layers = find_armor_layers(PACK_PATH)
print(f"🧭 พบ armor layer sets: {len(armor_layers)} เซ็ต (fallback ready)\n")

for i, armor in enumerate(item_type):
    item_json = f"pack/assets/minecraft/models/item/{armor}.json"
    overrides = process_json_file(item_json)

    for override in overrides:
        model = override.get("model")
        if not model:
            continue

        try:
            namespace, path = model.split(":")
            item = path.split("/")[-1]

            prop_file = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{namespace}_{item}.properties"
            if os.path.exists(prop_file):
                optifine.load(open(prop_file, "rb"))

                layer_key = f"texture.leather_layer_{2 if i == 2 else 1}"
                layer = None

                if optifine.get(layer_key):
                    layer = optifine.get(layer_key).data.split(".")[0]
                elif optifine.get(f"{layer_key}_overlay"):
                    layer = optifine.get(f"{layer_key}_overlay").data.split(".")[0]
                else:
                    print(f"⚠️ No layer info in {prop_file}")
                    continue

                src_texture = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{layer}.png"
                os.makedirs("staging/target/rp/textures/armor_layer", exist_ok=True)

                if os.path.exists(src_texture):
                    shutil.copy(src_texture, f"staging/target/rp/textures/armor_layer/{layer}.png")
                    print(f"🧩 Copied {layer}.png → armor_layer/")
                else:
                    print(f"⚠️ Missing armor texture: {src_texture}")
                    continue

            else:
                # =========================
                # 🔁 FALLBACK: No CIT found
                # =========================
                base = item.replace("_armor", "").replace("_layer", "")
                match = armor_layers.get(base)
                if not match:
                    print(f"⚠️ No matching fallback armor layer for {item}")
                    continue

                layer = base
                for layer_key, src in match.items():
                    if src:
                        dest = f"staging/target/rp/textures/armor_layer/{os.path.basename(src)}"
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        shutil.copy(src, dest)
                        print(f"🧩 [Fallback] Copied {os.path.basename(src)}")

            # 🔧 Generate attachable
            afile = f"staging/target/rp/attachables/{namespace}/{path}.json"
            if not os.path.exists(afile):
                os.makedirs(os.path.dirname(afile), exist_ok=True)
                with open(afile, "w") as f:
                    json.dump({}, f)

            gmdl = f"{item}_auto"

            atlas_texture_path = f"textures/armor_layer/{layer}.png"
            update_item_texture_json(gmdl, atlas_texture_path)

            icons_csv = "scratch_files/icons.csv"
            os.makedirs("scratch_files", exist_ok=True)
            with open(icons_csv, "a", encoding="utf-8") as f:
                f.write(f"{gmdl},{atlas_texture_path}\n")
            print(f"📌 Added icon to atlas: {gmdl} → {atlas_texture_path}")

            pfile = afile.replace(".json", ".player.json")
            write_armor(pfile, gmdl, layer, i)

        except Exception as e:
            print(f"❌ Error while processing {model}: {e}")
            continue
