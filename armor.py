import os
import json
import shutil
import glob
from jproperties import Properties

# ฟังก์ชันสำหรับประมวลผลไฟล์ JSON
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

# ฟังก์ชันสำหรับลบรายการที่ซ้ำกันใน geyser_mappings.json
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

# ฟังก์ชันหลักสำหรับการจัดการไฟล์ armor และ optifine
optifine = Properties()
i = 0
item_type = ["leather_helmet", "leather_chestplate", "leather_leggings", "leather_boots"]

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
        f.write(json.dumps(ajson))

# ตรวจสอบว่าไฟล์ geyser_mappings.json มีอยู่จริง
geyser_mappings_file = "staging/target/geyser_mappings.json"

if os.path.exists(geyser_mappings_file):
    print(f"File {geyser_mappings_file} found, proceeding with processing.")
    remove_duplicates_with_custom_model_data(geyser_mappings_file)
else:
    print(f"File {geyser_mappings_file} not found. Please check the download process.")

while i < 4:
    file_path = f"pack/assets/minecraft/models/item/{item_type[i]}.json"
    try:
        process_json_file(file_path)

        with open(file_path, "r") as f:
            data = json.load(f)
    except:
        i += 1
        continue

    # ตรวจสอบว่าเป็น format ใหม่ (range_dispatch) หรือไม่
    if "model" in data and isinstance(data["model"], dict) and data["model"].get("type") == "range_dispatch":
        entries = data["model"].get("entries", [])
        for entry in entries:
            try:
                # ดึงข้อมูลจาก entry
                custom_model_data = entry["threshold"]
                model_info = entry["model"]
                if model_info["type"] != "model":
                    continue
                    
                model = model_info["model"]
                # เพิ่ม prefix minecraft: ถ้าไม่มี namespace
                if ":" not in model:
                    model = "minecraft:" + model
                    
                namespace = model.split(":")[0]
                item = model.split("/")[-1]
                
                if item in item_type:
                    continue
                    
                path = model.split(":")[1] if ":" in model else model
                # Look for armor layer textures in model's directory first
                model_dir = os.path.dirname(f"pack/assets/{namespace}/models/{path}.json")
            except Exception as e:
                print(f"Error processing entry: {e}")
                print("Item not found...")
                continue
        else:
            try:
                path = model.split(":")[1]
                # Look for armor layer textures in model's directory first
                model_dir = os.path.dirname(f"pack/assets/{namespace}/models/{path}.json")
                texture_dir = model_dir.replace("/models/", "/textures/")
                
                # Try to find armor layer files
                layer_num = "2" if i == 2 else "1"
                layer = None
                layer_file = None
                
                # Search patterns for armor layers - CIT first, then other locations
                search_patterns = [
                    f"pack/assets/minecraft/optifine/cit/ia_generated_armors/*_layer_{layer_num}*.png",
                    f"{texture_dir}/*layer_{layer_num}*.png",
                    f"{texture_dir}/*armor_layer_{layer_num}*.png",
                    f"pack/assets/{namespace}/textures/**/*layer_{layer_num}*.png",
                    f"pack/assets/{namespace}/textures/**/*armor_layer_{layer_num}*.png"
                ]
                
                # Try each search pattern
                for pattern in search_patterns:
                    matches = glob.glob(pattern, recursive=True)
                    if matches:
                        layer_file = matches[0]
                        layer = os.path.splitext(os.path.basename(layer_file))[0]
                        break
                
                if layer is None:
                    raise FileNotFoundError(f"Could not find armor layer {layer_num} texture")

                # Create armor layer directory if it doesn't exist
                if not os.path.exists("staging/target/rp/textures/armor_layer"):
                    os.makedirs("staging/target/rp/textures/armor_layer")
                
                # Copy the found layer file
                if not os.path.exists(f"staging/target/rp/textures/armor_layer/{layer}.png"):
                    shutil.copy(
                        layer_file,
                        "staging/target/rp/textures/armor_layer"
                    )

                with open(f"pack/assets/{namespace}/models/{path}.json", "r") as f:
                    texture = json.load(f)["textures"]["layer1"]
                    tpath = texture.split(":")[1]
                    dest_path = f"staging/target/rp/textures/{namespace}/{path}.png"
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy(
                        f"pack/assets/{namespace}/textures/{tpath}.png", dest_path
                    )

                afile = glob.glob(
                    f"staging/target/rp/attachables/{namespace}/{path}*.json"
                )
                with open(afile[0], "r") as f:
                    da = json.load(f)["minecraft:attachable"]
                    gmdl = da["description"]["identifier"].split(":")[1]
                pfile = afile[0].replace(".json", ".player.json")
                write_armor(pfile, gmdl, layer, i)
            except Exception as e:
                print(e)
                print("Item not found...")
                continue
    i += 1
