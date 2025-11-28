import os
import json
import shutil
import glob
from jproperties import Properties

# ===============================
# 🔧 อัปเดต item_texture.json
# ===============================
def update_item_texture_json(gmdl_id, atlas_path):
    """อัปเดต path ของไอเท็มใน item_texture.json ให้ตรงกับไฟล์ที่ Python วาง"""
    item_texture_file = "staging/target/rp/textures/item_texture.json"

    if not os.path.exists(item_texture_file):
        print("⚠️ item_texture.json not found, creating new one.")
        os.makedirs(os.path.dirname(item_texture_file), exist_ok=True)
        data = {"resource_pack_name": "geyser_custom", "texture_name": "atlas.items", "texture_data": {}}
    else:
        with open(item_texture_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    tex = data.get("texture_data", {})
    tex[gmdl_id] = {"textures": atlas_path}
    data["texture_data"] = tex

    with open(item_texture_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"🔧 Updated item_texture.json: {gmdl_id} → {atlas_path}")


# ===============================
# 🔧 ฟังก์ชันล้าง override
# ===============================
def process_json_file(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
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

        item_types = [
            "minecraft:leather_helmet", "minecraft:leather_chestplate",
            "minecraft:leather_leggings", "minecraft:leather_boots",
            "minecraft:iron_helmet", "minecraft:iron_chestplate",
            "minecraft:iron_leggings", "minecraft:iron_boots",
            "minecraft:diamond_helmet", "minecraft:diamond_chestplate",
            "minecraft:diamond_leggings", "minecraft:diamond_boots",
            "minecraft:netherite_helmet", "minecraft:netherite_chestplate",
            "minecraft:netherite_leggings", "minecraft:netherite_boots"
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


# ===============================
# 🛡️ สร้าง attachable (CIT และ Equipment)
# ===============================
def write_armor(file, gmdl, layer, i):
    """สร้าง attachable สำหรับ leather armor (CIT)"""
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


def write_equipment_armor(file, gmdl, texture_path, i):
    type_map = ["helmet", "chestplate", "leggings", "boots"]
    armor_type = type_map[i]

    ajson = {
        "format_version": "1.10.0",
        "minecraft:attachable": {
            "description": {
                "identifier": f"geyser_custom:{gmdl}.player",
                "item": {f"geyser_custom:{gmdl}": "query.owner_identifier == 'minecraft:player'"},
                "materials": {
                    "default": "armor",
                    "enchanted": "armor_enchanted"
                },
                "textures": {
                    "default": texture_path,
                    "enchanted": "textures/misc/enchanted_item_glint"
                },
                "geometry": {"default": f"geometry.player.armor.{armor_type}"},
                "scripts": {"parent_setup": "variable.helmet_layer_visible = 0.0;"},
                "render_controllers": ["controller.render.armor"]
            }
        }
    }

    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "w") as f:
        json.dump(ajson, f, indent=4)

    print(f"✅ Generated equipment attachable: {file}")



# ===============================
# 📦 ประมวลผล Leather Armor (CIT)
# ===============================
def process_leather_armor():
    """ประมวลผล leather armor แบบเดิมด้วย CIT properties"""
    print("\n" + "="*60)
    print("🧪 Processing Leather Armor (CIT)")
    print("="*60)
    
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

                # โหลด .properties
                prop_file = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{namespace}_{item}.properties"
                if not os.path.exists(prop_file):
                    print(f"⚠️ Missing {prop_file}")
                    continue

                optifine.load(open(prop_file, "rb"))

                layer_key = f"texture.leather_layer_{2 if i == 2 else 1}"
                layer = None

                if optifine.get(layer_key):
                    layer = optifine.get(layer_key).data.split(".")[0]
                elif optifine.get(f"{layer_key}_overlay"):
                    layer = optifine.get(f"{layer_key}_overlay").data.split(".")[0]
                else:
                    print(f"⚠️ No layer info found in {prop_file}")
                    continue

                # Copy armor texture
                os.makedirs("staging/target/rp/textures/armor_layer", exist_ok=True)
                src_texture = f"pack/assets/minecraft/optifine/cit/ia_generated_armors/{layer}.png"

                if os.path.exists(src_texture):
                    shutil.copy(src_texture, f"staging/target/rp/textures/armor_layer/{layer}.png")
                    print(f"🧩 Copied {layer}.png → armor_layer/")
                else:
                    print(f"⚠️ Missing armor texture: {src_texture}")

                # Copy 2D icon
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

                # หา gmdl จาก attachable
                afile = glob.glob(f"staging/target/rp/attachables/{namespace}/{path}*.json")
                if not afile:
                    print(f"⚠️ No attachable found for {model}")
                    continue

                with open(afile[0], "r") as f:
                    da = json.load(f)["minecraft:attachable"]
                    gmdl = da["description"]["identifier"].split(":")[1]

                # Add icon → icons.csv
                atlas_texture_path = f"textures/{namespace}/{icon_texture}.png"

                icons_csv = "scratch_files/icons.csv"
                os.makedirs("scratch_files", exist_ok=True)

                with open(icons_csv, "a", encoding="utf-8") as f:
                    f.write(f"{gmdl},{atlas_texture_path}\n")

                print(f"📌 Added icon to atlas: {gmdl} → {atlas_texture_path}")

                # อัปเดต item_texture.json
                update_item_texture_json(gmdl, atlas_texture_path)

                # Generate player attachable
                pfile = afile[0].replace(".json", ".player.json")
                write_armor(pfile, gmdl, layer, i)

            except Exception as e:
                print(f"❌ Error while processing {model}: {e}")
                continue

def write_equipment_base(file, gmdl, texture_path, i):
    type_map = ["helmet", "chestplate", "leggings", "boots"]
    armor_type = type_map[i]

    ajson = {
        "format_version": "1.10.0",
        "minecraft:attachable": {
            "description": {
                "identifier": f"geyser_custom:{gmdl}",
                "materials": {
                    "default": "armor",
                    "enchanted": "armor_enchanted"
                },
                "textures": {
                    "default": texture_path,
                    "enchanted": "textures/misc/enchanted_item_glint"
                },
                "geometry": { "default": f"geometry.player.armor.{armor_type}" },
                "render_controllers": [ "controller.render.armor" ]
            }
        }
    }

    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "w") as f:
        json.dump(ajson, f, indent=4)

    print(f"🟦 Generated base attachable: {file}")
def find_existing_gmdl(namespace, armor_name, armor_piece):
    """
    ค้นหาไฟล์ attachable เดิมที่ IA auto-gen ไว้ในโฟลเดอร์ namespace ทั้งหมด
    และดึง gmdl จริงออกมา เช่น elder_boots.gmdl_0e76107
    """
    base_path = f"staging/target/rp/attachables/{namespace}"

    # ค้นทุกไฟล์ json ใน namespace และโฟลเดอร์ย่อย เช่น ia_auto_gen/*
    for file in glob.glob(base_path + "/**/*.json", recursive=True):
        if ".player" in file:
            continue

        # มักอยู่ในรูป items เช่น:
        # japan_armor_basickimono_helmet.gmdl_xxxxx.json
        filename = os.path.basename(file)

        if armor_name in filename and armor_piece in filename:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)["minecraft:attachable"]
                return data["description"]["identifier"].split(":")[1]

    return None

# ===============================
# 🛡️ ประมวลผล Netherite/Equipment Armor
# ===============================
def process_equipment_armor():
    """ประมวลผล Netherite/Equipment Armor ทั้งหมด"""
    print("\n" + "="*60)
    print("⚔️ Processing Equipment Armor (Netherite, etc.)")
    print("="*60)

    overlay_path = "pack/ia_overlay_1_21_2_plus/assets"

    if not os.path.exists(overlay_path):
        print(f"⚠️ Overlay path not found: {overlay_path}")
        return

    print(f"📁 Found overlay path: {overlay_path}")

    # หา namespace ทั้งหมดที่มี models/equipment
    namespaces_found = []
    for namespace in os.listdir(overlay_path):
        namespace_path = os.path.join(overlay_path, namespace)
        if not os.path.isdir(namespace_path):
            continue

        models_path = os.path.join(namespace_path, "models", "equipment")
        if os.path.exists(models_path):
            namespaces_found.append(namespace)

    print(f"🔍 Found {len(namespaces_found)} namespaces with equipment models: {namespaces_found}")

    if not namespaces_found:
        print("⚠️ No equipment models found!")
        return

    # ประมวลผลทีละ namespace
    for namespace in namespaces_found:
        namespace_path = os.path.join(overlay_path, namespace)
        models_path = os.path.join(namespace_path, "models", "equipment")

        for armor_file in glob.glob(os.path.join(models_path, "*.json")):
            armor_name = os.path.basename(armor_file).replace(".json", "")

            print(f"\n{'='*60}")
            print(f"🛡️ Processing: {namespace}:{armor_name}")
            print(f"{'='*60}")

            # โหลด model
            try:
                with open(armor_file, "r", encoding="utf-8") as f:
                    model_data = json.load(f)
            except Exception as e:
                print(f"❌ Failed to read model file: {e}")
                continue

            # =============================
            # ⭐ Extract humanoid + leggings
            # =============================
            layers = model_data.get("layers", {})

            humanoid_texture = None
            leggings_texture = None

            if isinstance(layers, dict):
                # humanoid
                if isinstance(layers.get("humanoid"), list):
                    for entry in layers["humanoid"]:
                        if "texture" in entry:
                            humanoid_texture = entry["texture"]
                            break
                # leggings
                if isinstance(layers.get("humanoid_leggings"), list):
                    for entry in layers["humanoid_leggings"]:
                        if "texture" in entry:
                            leggings_texture = entry["texture"]
                            break

            # =============================
            # ⭐ ทำชื่อไฟล์ปลายทาง
            # =============================
            humanoid_filename = f"{namespace}_{armor_name}_humanoid.png"
            leggings_filename = f"{namespace}_{armor_name}_leggings.png"

            dest_humanoid = os.path.join(
                "staging/target/rp/textures/equipment",
                humanoid_filename
            )
            dest_leggings = os.path.join(
                "staging/target/rp/textures/equipment",
                leggings_filename
            )

            # =============================
            # ⭐ Copy humanoid
            # =============================
            if humanoid_texture:
                tex_name = humanoid_texture.split(":")[1]
                src_humanoid = os.path.join(
                    namespace_path,
                    "textures/entity/equipment/humanoid",
                    tex_name + ".png"
                )
                if os.path.exists(src_humanoid):
                    shutil.copy(src_humanoid, dest_humanoid)
                    print(f"🧩 Copied humanoid texture → {dest_humanoid}")
                else:
                    print(f"⚠️ Humanoid texture not found: {src_humanoid}")
                    continue
            else:
                print("⚠️ No humanoid texture defined")
                continue

            # =============================
            # ⭐ Copy leggings
            # =============================
            if leggings_texture:
                tex_name = leggings_texture.split(":")[1]
                src_leggings = os.path.join(
                    namespace_path,
                    "textures/entity/equipment/humanoid_leggings",
                    tex_name + ".png"
                )
            else:
                src_leggings = src_humanoid  # ใช้ humanoid แทน

            if os.path.exists(src_leggings):
                shutil.copy(src_leggings, dest_leggings)
                print(f"🧩 Copied leggings texture → {dest_leggings}")
            else:
                print(f"⚠ leggings texture not found: {src_leggings}")

            # =============================
            # ⭐ หา override ใน item models (helmet/chesplate/leggings/boots)
            # =============================
            armor_types = ["netherite_helmet", "netherite_chestplate", "netherite_leggings", "netherite_boots"]

            for i, armor_type in enumerate(armor_types):
                item_json = f"pack/assets/minecraft/models/item/{armor_type}.json"

                if not os.path.exists(item_json):
                    continue

                with open(item_json, "r", encoding="utf-8") as f:
                    item_data = json.load(f)

                overrides = item_data.get("overrides", [])
                for override in overrides:
                    model = override.get("model", "")
                    if namespace in model and armor_name in model:
                        print(f"✅ Found matching override: {model}")

                        # หา icon
                        model_path = model.replace(":", "/")
                        model_json_path = f"pack/assets/{model_path}.json"

                        if not os.path.exists(model_json_path):
                            print(f"⚠️ Model file not found: {model_json_path}")
                            continue

                        with open(model_json_path, "r", encoding="utf-8") as f:
                            item_model = json.load(f)

                        # textures
                        tex = item_model.get("textures", {})
                        icon_texture = tex.get("layer0") or tex.get("layer1")

                        if not icon_texture:
                            print(f"⚠️ No icon texture found")
                            continue

                        # copy icon
                        if ":" in icon_texture:
                            icon_ns, icon_path = icon_texture.split(":")
                        else:
                            icon_ns = namespace
                            icon_path = icon_texture

                        src_icon = f"pack/assets/{icon_ns}/textures/{icon_path}.png"
                        dest_icon = f"staging/target/rp/textures/{icon_ns}/{icon_path}.png"

                        os.makedirs(os.path.dirname(dest_icon), exist_ok=True)
                        if os.path.exists(src_icon):
                            shutil.copy(src_icon, dest_icon)
                            print(f"🖼️ Copied icon → {dest_icon}")
                        else:
                            print(f"⚠️ Icon missing: {src_icon}")
                            continue
# ===============================
# 🧩 Auto-generate .player.json for ANY armor attachable
# ===============================
def auto_generate_player_attachables():
    print("\n" + "="*60)
    print("🛠️ Auto-generating .player.json ONLY for armors")
    print("="*60)

    base_path = "staging/target/rp/attachables"

    for namespace in os.listdir(base_path):
        ns_path = os.path.join(base_path, namespace)
        if not os.path.isdir(ns_path):
            continue

        attachable_files = glob.glob(ns_path + "/**/*.attachable.json", recursive=True)

        for file in attachable_files:
            filename = os.path.basename(file).lower()

            # ❌ Skip player files
            if filename.endswith(".attachable.player.json"):
                continue

            # ❌ Skip non-armor
            if not any(x in filename for x in ["helmet", "chestplate", "leggings", "boots"]):
                continue

            # Load attachable
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)["minecraft:attachable"]

            gmdl = data["description"]["identifier"].split(":")[1]

            # -------------------------------
            # ⭐ Determine armor type
            # -------------------------------
            if "helmet" in filename:
                armor_type = "helmet"
            elif "chestplate" in filename or "chest" in filename:
                armor_type = "chestplate"
            elif "leggings" in filename:
                armor_type = "leggings"
            else:
                armor_type = "boots"

            # -------------------------------
            # ⭐ Extract armor base name
            # filename: voidtech_boots.gmdl_xxx.attachable.json
            # → armor_base = voidtech
            # -------------------------------
            armor_base = filename.split(".gmdl_")[0]
            armor_base = armor_base.replace("_helmet", "") \
                                   .replace("_chestplate", "") \
                                   .replace("_leggings", "") \
                                   .replace("_boots", "")

            # -------------------------------
            # ⭐ Final texture path (MUST HAVE .png)
            # -------------------------------
            if armor_type == "leggings":
                final_texture = f"textures/equipment/{namespace}_{armor_base}_leggings.png"
            else:
                final_texture = f"textures/equipment/{namespace}_{armor_base}_humanoid.png"

            # -------------------------------
            # ⭐ Output file
            # -------------------------------
            player_file = file.replace(".attachable.json", ".attachable.player.json")

            player_json = {
                "format_version": "1.10.0",
                "minecraft:attachable": {
                    "description": {
                        "identifier": f"geyser_custom:{gmdl}.player",
                        "item": {f"geyser_custom:{gmdl}": "query.owner_identifier == 'minecraft:player'"},
                        "materials": {
                            "default": "armor",
                            "enchanted": "armor_enchanted"
                        },
                        "textures": {
                            "default": final_texture,
                            "enchanted": "textures/misc/enchanted_item_glint"
                        },
                        "geometry": {
                            "default": f"geometry.player.armor.{armor_type}"
                        },
                        "scripts": {"parent_setup": "variable.helmet_layer_visible = 0.0;"},
                        "render_controllers": ["controller.render.armor"]
                    }
                }
            }

            os.makedirs(os.path.dirname(player_file), exist_ok=True)
            with open(player_file, "w", encoding="utf-8") as f:
                json.dump(player_json, f, indent=4)

            print(f"🧩 Generated armor player attachable → {player_file}")

# ===============================
# 🚀 MAIN START
# ===============================
geyser_mappings_file = "staging/target/geyser_mappings.json"
if os.path.exists(geyser_mappings_file):
    remove_duplicates_with_custom_model_data(geyser_mappings_file)

# ประมวลผล Leather Armor
process_leather_armor()

# ประมวลผล Equipment Armor (Netherite, etc.)
process_equipment_armor()
auto_generate_player_attachables()
print("\n" + "="*60)
print("✅ All armor processing complete!")
print("="*60)
