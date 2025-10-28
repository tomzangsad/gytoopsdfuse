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

# -----------------------------
# 🧩 ฟังก์ชันสำหรับประมวลผลไฟล์ JSON
# -----------------------------
def process_json_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r') as f:
        data = json.load(f)

    overrides = data.get("overrides", [])
    processed_overrides = []
    seen_custom_model_data = set()

    for override in overrides:
        predicate = override.get("predicate", {})
        model = override.get("model", "")

        # ลบ override ที่มี trim_type
        if "trim_type" in predicate:
            continue

        # ตรวจสอบ custom_model_data
        custom_model_data = predicate.get("custom_model_data")
        if custom_model_data is not None:
            # เก็บเฉพาะอันแรกของ custom_model_data ที่เจอ
            if custom_model_data in seen_custom_model_data:
                continue
            seen_custom_model_data.add(custom_model_data)

        processed_overrides.append(override)

    # อัปเดต overrides ในไฟล์
    data["overrides"] = processed_overrides

    # เขียนผลลัพธ์กลับไปยังไฟล์เดิม
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Processed {file_path}")


# -----------------------------
# 🧩 ลบรายการที่ซ้ำใน geyser_mappings.json
# -----------------------------
def remove_duplicates_with_custom_model_data(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        item_types = [
            "minecraft:leather_helmet",
            "minecraft:leather_chestplate",
            "minecraft:leather_leggings",
            "minecraft:leather_boots",
        ]

        for item_type in item_types:
            if item_type in data:
                unique_entries = {}
                for entry in data[item_type]:
                    custom_model_data = entry.get("custom_model_data")
                    if custom_model_data not in unique_entries:
                        unique_entries[custom_model_data] = entry

                data[item_type] = list(unique_entries.values())

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Processed {file_path} successfully.")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


# -----------------------------
# 🧩 เขียนไฟล์ armor player.json
# -----------------------------
def write_armor(file, gmdl, layer, i):
    type_map = ["helmet", "chestplate", "leggings", "boots"]
    type = type_map[i]
    ajson = {
        "format_version": "1.10.0",
        "minecraft:attachable": {
            "description": {
                "identifier": f"geyser_custom:{gmdl}.player",
                "item": {
                    f"geyser_custom:{gmdl}": "query.owner_identifier == 'minecraft:player'"
                },
                "materials": {
                    "default": "armor_leather",
                    "enchanted": "armor_leather_enchanted",
                },
                "textures": {
                    "default": f"textures/armor_layer/{layer}",
                    "enchanted": "textures/misc/enchanted_item_glint",
                },
                "geometry": {
                    "default": f"geometry.player.armor.{type}",
                },
                "scripts": {
                    "parent_setup": "variable.helmet_layer_visible = 0.0;",
                },
                "render_controllers": ["controller.render.armor"],
            },
        },
    }
    with open(file, "w") as f:
        f.write(json.dumps(ajson, indent=4))


# -----------------------------
# 🧩 เริ่มทำงาน
# -----------------------------
optifine = Properties()
i = 0
item_type = ["leather_helmet", "leather_chestplate", "leather_leggings", "leather_boots"]

geyser_mappings_file = "staging/target/geyser_mappings.json"
if os.path.exists(geyser_mappings_file):
    print(f"File {geyser_mappings_file} found, proceeding with processing.")
    remove_duplicates_with_custom_model_data(geyser_mappings_file)
else:
    print(f"File {geyser_mappings_file} not found. Please check the download process.")


# -----------------------------
# 🧩 วนลูป armor 4 ชนิด
# -----------------------------
while i < 4:
    # พยายามหาทุก namespace
    search_pattern = f"pack/assets/**/models/item/{item_type[i]}.json"
    matches = glob.glob(search_pattern, recursive=True)
    
    if matches:
        file_path = matches[0]
    else:
        print(f"⚠️ No model file found for {item_type[i]}, skipping...")
        i += 1
        continue
    try:
        process_json_file(file_path)
        with open(file_path, "r") as f:
            data = json.load(f)
    except:
        i += 1
        continue

    for override in data["overrides"]:
        custom_model_data = override["predicate"]["custom_model_data"]
        model = override["model"]
        namespace = model.split(":")[0]
        item = model.split("/")[-1]
        if item in item_type:
            continue
        else:
            try:
                path = model.split(":")[1]
                optifine_file = f"{namespace}_{item}"
                prop_path = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{optifine_file}.properties"

                # ---------------------------------------------
                # 🟩 1. ถ้ามีไฟล์ .properties (CIT)
                # ---------------------------------------------
                if os.path.exists(prop_path):
                    with open(prop_path, "rb") as f:
                        optifine.load(f)
                        layer = optifine.get(f"texture.leather_layer_{2 if i == 2 else 1}").data.split(".")[0]
                else:
                    # ---------------------------------------------
                    # 🟦 2. ไม่มี CIT → หา texture armor layer เอง
                    # ---------------------------------------------
                    print(f"No .properties found for {item}, searching for armor layer textures...")

                    # หาไฟล์ layer ที่น่าจะเกี่ยวข้อง
                    possible_layers = glob.glob("pack/assets/minecraft/textures/**/*.png", recursive=True)
                    layer = None
                    for lay in possible_layers:
                        name = os.path.basename(lay).lower()
                        if (
                            "_armor_layer" in name
                            and item.split("_")[0] in name
                        ):
                            layer = os.path.splitext(os.path.basename(lay))[0]
                            source_layer_path = lay
                            break

                    if not layer:
                        # ถ้าไม่เจอเลย → หา layer_1 เริ่มต้นแทน
                        fallback = [p for p in possible_layers if "armor_layer_1" in os.path.basename(p)]
                        if fallback:
                            layer = os.path.splitext(os.path.basename(fallback[0]))[0]
                            source_layer_path = fallback[0]
                        else:
                            raise FileNotFoundError("No armor_layer texture found anywhere.")

                    # ✅ คัดลอกไฟล์ layer ที่หาเจอ
                    os.makedirs("staging/target/rp/textures/armor_layer", exist_ok=True)
                    shutil.copy(source_layer_path, f"staging/target/rp/textures/armor_layer/{os.path.basename(source_layer_path)}")
                    print(f"Copied armor layer: {layer}")

                # ---------------------------------------------
                # 🟧 คัดลอก texture ของตัว model armor
                # ---------------------------------------------
                with open(f"pack/assets/{namespace}/models/{path}.json", "r") as f:
                    texture = json.load(f)["textures"]["layer1"]
                    tpath = texture.split(":")[1]
                    dest_path = f"staging/target/rp/textures/{namespace}/{path}.png"
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy(f"pack/assets/{namespace}/textures/{tpath}.png", dest_path)

                # ---------------------------------------------
                # 🟥 สร้างไฟล์ .player.json สำหรับ Geyser
                # ---------------------------------------------
                # 🔍 ค้นหาไฟล์ attachable ให้ครอบคลุมทุก subfolder
                afile = glob.glob(f"staging/target/rp/attachables/{namespace}/**/{path.split('/')[-1]}*.json", recursive=True)
                
                if not afile:
                    print(f"⚠️ No attachable found for {item}, generating new attachable...")
                    attach_dir = f"staging/target/rp/attachables/{namespace}/{os.path.dirname(path)}"
                    os.makedirs(attach_dir, exist_ok=True)
                
                    base_attachable = {
                        "format_version": "1.10.0",
                        "minecraft:attachable": {
                            "description": {
                                "identifier": f"geyser_custom:{item}",
                                "materials": {
                                    "default": "armor_leather",
                                    "enchanted": "armor_leather_enchanted",
                                },
                                "textures": {
                                    "default": f"textures/armor_layer/{layer}",
                                    "enchanted": "textures/misc/enchanted_item_glint",
                                },
                                "geometry": {
                                    "default": f"geometry.player.armor.{['helmet','chestplate','leggings','boots'][i]}",
                                },
                                "render_controllers": ["controller.render.armor"],
                            }
                        }
                    }
                
                    attach_path = f"{attach_dir}/{item}.json"
                    with open(attach_path, "w") as f:
                        json.dump(base_attachable, f, indent=4)
                    afile = [attach_path]
                    print(f"🆕 Created base attachable: {attach_path}")
                
                # ✅ โหลด attachable และสร้าง .player.json
                with open(afile[0], "r") as f:
                    da = json.load(f)["minecraft:attachable"]
                    gmdl = da["description"]["identifier"].split(":")[1]

                
                pfile = afile[0].replace(".json", ".player.json")
                write_armor(pfile, gmdl, layer, i)
                print(f"✅ Generated armor: {item} → {pfile}")

            except Exception as e:
                print(f"❌ Error processing {item}: {e}")
                continue
    i += 1
