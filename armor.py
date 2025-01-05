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
                "item": {f"geyser_custom:{gmdl}": "query.owner_identifier == 'minecraft:player'"},
                "materials": {
                    "default": "armor_leather",
                    "enchanted": "armor_leather_enchanted"
                },
                "textures": {
                    "default": f"textures/armor_layer/{layer}",
                    "enchanted": "textures/misc/enchanted_item_glint"
                },
                "geometry": {
                    "default": f"geometry.player.armor.{type}"
                },
                "scripts": {
                    "parent_setup": "variable.helmet_layer_visible = 0.0;"
                },
                "render_controllers": ["controller.render.armor"]
            }
        }
    }
    with open(file, "w") as f:
        f.write(json.dumps(ajson))


while i < 4:
    file_path = f"pack/assets/minecraft/models/item/{item_type[i]}.json"
    try:
        # ประมวลผลไฟล์ JSON
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
                with open(f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{optifine_file}.properties", "rb") as f:
                    optifine.load(f)
                    layer = optifine.get(f"texture.leather_layer_{2 if i == 2 else 1}").data.split(".")[0]

                if not os.path.exists("staging/target/rp/textures/armor_layer"):
                    os.makedirs("staging/target/rp/textures/armor_layer")
                if not os.path.exists(f"staging/target/rp/textures/armor_layer/{layer}.png"):
                    shutil.copy(f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{layer}.png", "staging/target/rp/textures/armor_layer")

                with open(f"pack/assets/{namespace}/models/{path}.json", "r") as f:
                    texture = json.load(f)["textures"]["layer1"]
                    tpath = texture.split(":")[1]
                    dest_path = f"staging/target/rp/textures/{namespace}/{path}.png"
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy(f"pack/assets/{namespace}/textures/{tpath}.png", dest_path)

                afile = glob.glob(f"staging/target/rp/attachables/{namespace}/{path}*.json")
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
