# import os
# import json
# import shutil
# import glob
# from jproperties import Properties

# # ฟังก์ชันสำหรับประมวลผลไฟล์ JSON
# def process_json_file(file_path):
#     if not os.path.exists(file_path):
#         print(f"File not found: {file_path}")
#         return

#     with open(file_path, 'r') as f:
#         data = json.load(f)

#     overrides = data.get("overrides", [])
#     processed_overrides = []
#     seen_custom_model_data = set()

#     for override in overrides:
#         predicate = override.get("predicate", {})
#         model = override.get("model", "")

#         # ลบ override ที่มี trim_type
#         if "trim_type" in predicate:
#             continue

#         # ตรวจสอบ custom_model_data
#         custom_model_data = predicate.get("custom_model_data")
#         if custom_model_data is not None:
#             # เก็บเฉพาะอันแรกของ custom_model_data ที่เจอ
#             if custom_model_data in seen_custom_model_data:
#                 continue
#             seen_custom_model_data.add(custom_model_data)

#         processed_overrides.append(override)

#     # อัปเดต overrides ในไฟล์
#     data["overrides"] = processed_overrides

#     # เขียนผลลัพธ์กลับไปยังไฟล์เดิม
#     with open(file_path, 'w') as f:
#         json.dump(data, f, indent=4)
#     print(f"Processed {file_path}")

# # ฟังก์ชันสำหรับลบรายการที่ซ้ำกันใน geyser_mappings.json
# def remove_duplicates_with_custom_model_data(file_path):
#     try:
#         with open(file_path, 'r') as f:
#             data = json.load(f)

#         item_types = [
#             "minecraft:leather_helmet",
#             "minecraft:leather_chestplate",
#             "minecraft:leather_leggings",
#             "minecraft:leather_boots",
#         ]

#         for item_type in item_types:
#             if item_type in data:
#                 unique_entries = {}
#                 for entry in data[item_type]:
#                     custom_model_data = entry.get("custom_model_data")
#                     if custom_model_data not in unique_entries:
#                         unique_entries[custom_model_data] = entry

#                 data[item_type] = list(unique_entries.values())

#         with open(file_path, 'w') as f:
#             json.dump(data, f, indent=4)
#         print(f"Processed {file_path} successfully.")
#     except Exception as e:
#         print(f"Error processing {file_path}: {e}")

# # ฟังก์ชันหลักสำหรับการจัดการไฟล์ armor และ optifine
# optifine = Properties()
# i = 0
# item_type = ["leather_helmet", "leather_chestplate", "leather_leggings", "leather_boots"]

# def write_armor(file, gmdl, layer, i):
#     type_map = ["helmet", "chestplate", "leggings", "boots"]
#     type = type_map[i]
#     ajson = {
#         "format_version": "1.10.0",
#         "minecraft:attachable": {
#             "description": {
#                 "identifier": f"geyser_custom:{gmdl}.player",
#                 "item": {
#                     f"geyser_custom:{gmdl}": "query.owner_identifier == 'minecraft:player'"
#                 },
#                 "materials": {
#                     "default": "armor_leather",
#                     "enchanted": "armor_leather_enchanted",
#                 },
#                 "textures": {
#                     "default": f"textures/armor_layer/{layer}",
#                     "enchanted": "textures/misc/enchanted_item_glint",
#                 },
#                 "geometry": {
#                     "default": f"geometry.player.armor.{type}",
#                 },
#                 "scripts": {
#                     "parent_setup": "variable.helmet_layer_visible = 0.0;",
#                 },
#                 "render_controllers": ["controller.render.armor"],
#             },
#         },
#     }
#     with open(file, "w") as f:
#         f.write(json.dumps(ajson))

# # ตรวจสอบว่าไฟล์ geyser_mappings.json มีอยู่จริง
# geyser_mappings_file = "staging/target/geyser_mappings.json"

# if os.path.exists(geyser_mappings_file):
#     print(f"File {geyser_mappings_file} found, proceeding with processing.")
#     remove_duplicates_with_custom_model_data(geyser_mappings_file)
# else:
#     print(f"File {geyser_mappings_file} not found. Please check the download process.")

# while i < 4:
#     file_path = f"pack/assets/minecraft/models/item/{item_type[i]}.json"
#     try:
#         process_json_file(file_path)

#         with open(file_path, "r") as f:
#             data = json.load(f)
#     except:
#         i += 1
#         continue

#     for override in data["overrides"]:
#         custom_model_data = override["predicate"]["custom_model_data"]
#         model = override["model"]
#         namespace = model.split(":")[0]
#         item = model.split("/")[-1]
#         if item in item_type:
#             continue
#         else:
#             try:
#                 path = model.split(":")[1]
#                 optifine_file = f"{namespace}_{item}"
#                 with open(f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{optifine_file}.properties", "rb") as f:
#                     optifine.load(f)
#                     layer = optifine.get(f"texture.leather_layer_{2 if i == 2 else 1}").data.split(".")[0]

#                 if not os.path.exists("staging/target/rp/textures/armor_layer"):
#                     os.makedirs("staging/target/rp/textures/armor_layer")
#                 if not os.path.exists(f"staging/target/rp/textures/armor_layer/{layer}.png"):
#                     shutil.copy(
#                         f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{layer}.png",
#                         "staging/target/rp/textures/armor_layer",
#                     )

#                 with open(f"pack/assets/{namespace}/models/{path}.json", "r") as f:
#                     texture = json.load(f)["textures"]["layer1"]
#                     tpath = texture.split(":")[1]
#                     dest_path = f"staging/target/rp/textures/{namespace}/{path}.png"
#                     os.makedirs(os.path.dirname(dest_path), exist_ok=True)
#                     shutil.copy(
#                         f"pack/assets/{namespace}/textures/{tpath}.png", dest_path
#                     )

#                 afile = glob.glob(
#                     f"staging/target/rp/attachables/{namespace}/{path}*.json"
#                 )
#                 with open(afile[0], "r") as f:
#                     da = json.load(f)["minecraft:attachable"]
#                     gmdl = da["description"]["identifier"].split(":")[1]
#                 pfile = afile[0].replace(".json", ".player.json")
#                 write_armor(pfile, gmdl, layer, i)
#             except Exception as e:
#                 print(e)
#                 print("Item not found...")
#                 continue
#     i += 1





import os
import json
import shutil
import glob
from jproperties import Properties

# ===============================
# 🔧 ฟังก์ชันพื้นฐาน
# ===============================
def process_json_file(file_path):
    """ล้างข้อมูล override ซ้ำ / trim_type ออกจากไฟล์ item"""
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
    """ลบข้อมูลซ้ำใน geyser_mappings.json"""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        item_types = [
            "minecraft:leather_helmet",
            "minecraft:leather_chestplate",
            "minecraft:leather_leggings",
            "minecraft:leather_boots",
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
    except Exception as e:
        print(f"⚠️ Error cleaning {file_path}: {e}")


def write_armor(file, gmdl, layer, i):
    """สร้างไฟล์ armor.attachable player"""
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


# ===============================
# 🚀 เริ่มการประมวลผลหลัก
# ===============================
geyser_mappings_file = "staging/target/geyser_mappings.json"
if os.path.exists(geyser_mappings_file):
    remove_duplicates_with_custom_model_data(geyser_mappings_file)
else:
    print("⚠️ geyser_mappings.json not found, skipping duplicate cleanup.")

optifine = Properties()
item_type = ["leather_helmet", "leather_chestplate", "leather_leggings", "leather_boots"]

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

            # ==========================
            # 📘 โหลด .properties ของ armor
            # ==========================
            prop_file = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{namespace}_{item}.properties"
            if not os.path.exists(prop_file):
                print(f"⚠️ Missing {prop_file}")
                continue

            optifine.load(open(prop_file, "rb"))

            # อ่าน layer จาก properties (รองรับ overlay)
            layer_key = f"texture.leather_layer_{2 if i == 2 else 1}"
            layer = None
            if optifine.get(layer_key):
                layer = optifine.get(layer_key).data.split(".")[0]
            elif optifine.get(f"{layer_key}_overlay"):
                layer = optifine.get(f"{layer_key}_overlay").data.split(".")[0]
            else:
                print(f"⚠️ No layer info found in {prop_file}")
                continue

            # ==========================
            # 🧩 Copy armor texture
            # ==========================
            os.makedirs("staging/target/rp/textures/armor_layer", exist_ok=True)
            src_texture = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{layer}.png"
            if os.path.exists(src_texture):
                shutil.copy(src_texture, f"staging/target/rp/textures/armor_layer/{layer}.png")
                print(f"🧩 Copied {layer}.png → armor_layer/")
            else:
                print(f"⚠️ Texture missing: {src_texture}")

            # ==========================
            # 🔎 หา attachable เดิมเพื่อสร้าง .player.json
            # ==========================
            afile = glob.glob(f"staging/target/rp/attachables/{namespace}/{path}*.json")
            if not afile:
                print(f"⚠️ No attachable found for {model}")
                continue

            with open(afile[0], "r") as f:
                da = json.load(f)["minecraft:attachable"]
                gmdl = da["description"]["identifier"].split(":")[1]

            pfile = afile[0].replace(".json", ".player.json")
            write_armor(pfile, gmdl, layer, i)

        except Exception as e:
            print(f"❌ Error while processing {model}: {e}")
            continue
