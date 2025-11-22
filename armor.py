
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
#             "minecraft:iron_helmet",
#             "minecraft:iron_chestplate",
#             "minecraft:iron_leggings",
#             "minecraft:iron_boots",
#             "minecraft:diamond_helmet",
#             "minecraft:diamond_chestplate",
#             "minecraft:diamond_leggings",
#             "minecraft:diamond_boots",
#             "minecraft:netherite_helmet",
#             "minecraft:netherite_chestplate",
#             "minecraft:netherite_leggings",
#             "minecraft:netherite_boots"
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
# item_type = ["leather_helmet", "leather_chestplate", "leather_leggings", "leather_boots",
#             "iron_helmet", "iron_chestplate", "iron_leggings", "iron_boots",
#             "diamond_helmet", "diamond_chestplate", "diamond_leggings", "diamond_boots",
#             "netherite_helmet", "netherite_chestplate", "netherite_leggings", "netherite_boots",
#             "chainmail_helmet", "chainmail_chestplate", "chainmail_leggings", "chainmail_boots"]

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
# 🔧 ล้าง override
# ===============================
def process_json_file(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return []

    with open(file_path, "r") as f:
        data = json.load(f)

    overrides = data.get("overrides", [])
    processed = []
    seen_cmd = set()

    for override in overrides:
        predicate = override.get("predicate", {})

        if "trim_type" in predicate:
            continue

        cmd = predicate.get("custom_model_data")
        if cmd is not None:
            if cmd in seen_cmd:
                continue
            seen_cmd.add(cmd)

        processed.append(override)

    data["overrides"] = processed
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Cleaned {file_path}")
    return processed


# ===============================
# 🧱 เขียนไฟล์ player attachable
# ===============================
def write_armor(file, gmdl, layer, armor_type):
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


# ===============================
# 🚀 MAIN
# ===============================
optifine = Properties()

item_type = [
    "leather_helmet", "leather_chestplate", "leather_leggings", "leather_boots",
    "iron_helmet", "iron_chestplate", "iron_leggings", "iron_boots",
    "diamond_helmet", "diamond_chestplate", "diamond_leggings", "diamond_boots",
    "netherite_helmet", "netherite_chestplate", "netherite_leggings", "netherite_boots",
    "chainmail_helmet", "chainmail_chestplate", "chainmail_leggings", "chainmail_boots"
]

type_map = {
    0: "helmet", 1: "chestplate", 2: "leggings", 3: "boots"
}

for i, armor in enumerate(item_type):

    # index แบบเกราะ 4 ชิ้น (0-3 เท่านั้น)
    armor_index = i % 4
    armor_type = type_map[armor_index]

    item_json = f"pack/assets/minecraft/models/item/{armor}.json"
    overrides = process_json_file(item_json)

    for override in overrides:

        model = override.get("model")
        if not model:
            continue

        try:
            namespace, path = model.split(":")
            item = path.split("/")[-1]

            # -----------------------------
            # หาวัสดุ armor เช่น leather/iron/diamond/chainmail
            # -----------------------------
            material = armor.split("_")[0]
            if material == "chainmail":
                material = "chain"

            # -----------------------------
            # หา layer index
            # -----------------------------
            layer_index = 2 if armor_type == "leggings" else 1

            # -----------------------------
            # CIT properties file path
            # -----------------------------
            prop_file = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{namespace}_{item}.properties"

            # ==========================
            # ⭐ Fallback: ไม่มี CIT → หา layer_x.png ทั้ง pack
            # ==========================
            if not os.path.exists(prop_file):
                print(f"⚠️ Missing {prop_file} → scanning pack for fallback textures…")

                armor_base = armor.replace("_helmet","").replace("_chestplate","") \
                                  .replace("_leggings","").replace("_boots","")

                layer_1 = layer_2 = None

                for root, dirs, files in os.walk("pack"):
                    for file in files:
                        if file == f"{armor_base}_layer_1.png":
                            layer_1 = os.path.join(root, file)
                        if file == f"{armor_base}_layer_2.png":
                            layer_2 = os.path.join(root, file)

                if not layer_1 or not layer_2:
                    print(f"❌ Fallback failed: No layer textures for {armor_base}")
                    continue

                # Copy both layers
                os.makedirs("staging/target/rp/textures/armor_layer", exist_ok=True)

                out1 = f"staging/target/rp/textures/armor_layer/{armor_base}_layer_1.png"
                out2 = f"staging/target/rp/textures/armor_layer/{armor_base}_layer_2.png"

                shutil.copy(layer_1, out1)
                shutil.copy(layer_2, out2)

                print(f"🧩 Fallback copied → {out1}")
                print(f"🧩 Fallback copied → {out2}")

                layer = f"{armor_base}_layer_{layer_index}"

            else:
                # ==========================
                # ใช้ CIT ตามปกติ
                # ==========================
                optifine.load(open(prop_file, "rb"))

                layer_key = f"texture.{material}_layer_{layer_index}"
                layer = None

                if optifine.get(layer_key):
                    layer = optifine.get(layer_key).data.split(".")[0]
                elif optifine.get(f"{layer_key}_overlay"):
                    layer = optifine.get(f"{layer_key}_overlay").data.split(".")[0]
                else:
                    print(f"⚠️ No layer info in {prop_file}")
                    continue

                # Copy armor texture
                os.makedirs("staging/target/rp/textures/armor_layer", exist_ok=True)
                src_texture = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{layer}.png"

                if os.path.exists(src_texture):
                    shutil.copy(src_texture, f"staging/target/rp/textures/armor_layer/{layer}.png")
                    print(f"🧩 Copied {layer}.png → armor_layer/")
                else:
                    print(f"⚠️ Missing armor texture: {src_texture}")

            # -----------------------------
            # ICON COPY
            # -----------------------------
            model_json_path = f"pack/assets/{namespace}/models/{path}.json"

            if not os.path.exists(model_json_path):
                print(f"⚠️ Missing model file: {model_json_path}")
                continue

            with open(model_json_path, "r") as f:
                model_data = json.load(f)

            textures = model_data.get("textures", {})
            icon_texture = textures.get("layer0") or textures.get("layer1")

            if icon_texture == "item/empty" and textures.get("layer1"):
                icon_texture = textures["layer1"]

            if ":" in icon_texture:
                icon_texture = icon_texture.split(":")[1]

            src_icon = f"pack/assets/{namespace}/textures/{icon_texture}.png"
            dest_icon = f"staging/target/rp/textures/{namespace}/{icon_texture}.png"

            os.makedirs(os.path.dirname(dest_icon), exist_ok=True)

            if os.path.exists(src_icon):
                shutil.copy(src_icon, dest_icon)
                print(f"🖼️ Copied item icon → {dest_icon}")
            else:
                print(f"⚠️ Missing icon texture: {src_icon}")
                continue

            # -----------------------------
            # หา gmdl จาก attachable
            # -----------------------------
            afile = glob.glob(f"staging/target/rp/attachables/{namespace}/{path}*.json")
            if not afile:
                print(f"⚠️ No attachable found for {model}")
                continue

            with open(afile[0], "r") as f:
                da = json.load(f)["minecraft:attachable"]
                gmdl = da["description"]["identifier"].split(":")[1]

            # -----------------------------
            # icons.csv
            # -----------------------------
            atlas_texture_path = f"textures/{namespace}/{icon_texture}.png"
            os.makedirs("scratch_files", exist_ok=True)

            with open("scratch_files/icons.csv", "a", encoding="utf-8") as f:
                f.write(f"{gmdl},{atlas_texture_path}\n")

            print(f"📌 Added icon: {gmdl}")

            # -----------------------------
            # item_texture.json
            # -----------------------------
            update_item_texture_json(gmdl, atlas_texture_path)

            # -----------------------------
            # Generate .player.json
            # -----------------------------
            pfile = afile[0].replace(".json", ".player.json")
            write_armor(pfile, gmdl, layer, armor_type)

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

