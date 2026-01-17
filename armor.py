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
                "item": {f"geyser_custom:{gmdl}": True},
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
                "item": {f"geyser_custom:{gmdl}": True},
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
    """ประมวลผล Netherite และ armor อื่นๆ ที่ใช้ equipment model"""
    print("\n" + "="*60)
    print("⚔️ Processing Equipment Armor (Netherite, etc.)")
    print("="*60)
    
    overlay_path = "pack/ia_overlay_1_21_2_plus/assets"
    
    if not os.path.exists(overlay_path):
        print(f"⚠️ Overlay path not found: {overlay_path}")
        return
    
    print(f"📁 Found overlay path: {overlay_path}")
    
    # วนหา namespace folders
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
    
    # วนหา namespace folders
    for namespace in namespaces_found:
        namespace_path = os.path.join(overlay_path, namespace)
        if not os.path.isdir(namespace_path):
            continue
            
        models_path = os.path.join(namespace_path, "models", "equipment")
        if not os.path.exists(models_path):
            continue
            
        # หาไฟล์ .json ทั้งหมด
        for armor_file in glob.glob(os.path.join(models_path, "*.json")):
            armor_name = os.path.basename(armor_file).replace(".json", "")
            
            print(f"\n{'='*60}")
            print(f"🛡️ Processing: {namespace}:{armor_name}")
            print(f"{'='*60}")
            
            # อ่านไฟล์ model
            try:
                with open(armor_file, "r", encoding="utf-8") as f:
                    model_data = json.load(f)
                    
                print(f"📄 Model structure: {json.dumps(model_data, indent=2)[:500]}...")  # แสดง 500 ตัวอักษรแรก
            except Exception as e:
                print(f"❌ Failed to read model file: {e}")
                continue
            
            # หา texture paths
            layers = model_data.get("layers", {})

            humanoid_texture = None
            leggings_texture = None
            
            # --- CASE 1: New IA format (list inside keys) ---
            layers = model_data.get("layers", {})

            humanoid_texture = None
            leggings_texture = None
            
            if isinstance(layers, dict):
            
                # humanoid
                if isinstance(layers.get("humanoid"), list):
                    for entry in layers["humanoid"]:
                        if isinstance(entry, dict) and entry.get("texture"):
                            humanoid_texture = entry["texture"]
                            break
                else:
                    humanoid_texture = layers.get("humanoid", {}).get("texture")
            
                # leggings
                if isinstance(layers.get("humanoid_leggings"), list):
                    for entry in layers["humanoid_leggings"]:
                        if isinstance(entry, dict) and entry.get("texture"):
                            leggings_texture = entry["texture"]
                            break
                else:
                    leggings_texture = layers.get("humanoid_leggings", {}).get("texture")
            
            elif isinstance(layers, list):
                for entry in layers:
                    if not isinstance(entry, dict):
                        continue
                    if "humanoid" in str(entry):
                        humanoid_texture = entry.get("texture")
                    if "leggings" in str(entry):
                        leggings_texture = entry.get("texture")


            
            if not humanoid_texture:
                print(f"⚠️ No humanoid texture found")
                continue
            
            # Copy textures (ใช้ path จาก namespace_path ที่มี pack/ อยู่แล้ว)
            textures_base = namespace_path  # เช่น pack/ia_overlay_1_21_2_plus/assets/3b_soul_skull
            
            # Humanoid texture
            # Extract filename from namespace:texture
            tex_name = humanoid_texture.split(":")[1]
            
            # IA Overlay 1.21.2+ path
            src_humanoid = os.path.join(
                textures_base,
                "textures", "entity", "equipment", "humanoid",
                tex_name + ".png"
            )

            dest_humanoid = os.path.join(
                "staging/target/rp/textures/equipment",
                f"{namespace}_{armor_name}_humanoid.png"
            )

            
            os.makedirs(os.path.dirname(dest_humanoid), exist_ok=True)
            
            if os.path.exists(src_humanoid):
                shutil.copy(src_humanoid, dest_humanoid)
                print(f"🧩 Copied humanoid texture → {dest_humanoid}")
            else:
                print(f"⚠️ Humanoid texture not found: {src_humanoid}")
                continue
            
            # Leggings texture
            # Leggings texture
            if leggings_texture:
                tex_name = leggings_texture.split(":")[1]
                src_leggings = os.path.join(
                    textures_base,
                    "textures", "entity", "equipment", "humanoid_leggings",
                    tex_name + ".png"
                )
            else:
                src_leggings = src_humanoid
            
            dest_leggings = os.path.join(
                "staging/target/rp/textures/equipment",
                f"{namespace}_{armor_name}_leggings.png"
            )
            
            # copy leggings texture
            os.makedirs(os.path.dirname(dest_leggings), exist_ok=True)
            
            if os.path.exists(src_leggings):
                shutil.copy(src_leggings, dest_leggings)
                print(f"🧩 Copied leggings texture → {dest_leggings}")
            else:
                print(f"⚠ leggings texture not found: {src_leggings}")
                dest_leggings = dest_humanoid


            
            # ประมวลผลแต่ละชิ้นส่วนเกราะ
            armor_types = ["netherite_helmet", "netherite_chestplate", "netherite_leggings", "netherite_boots"]
            
            for i, armor_type in enumerate(armor_types):
                item_json = f"pack/assets/minecraft/models/item/{armor_type}.json"
                
                if not os.path.exists(item_json):
                    continue
                
                # อ่าน overrides
                with open(item_json, "r", encoding="utf-8") as f:
                    item_data = json.load(f)
                
                overrides = item_data.get("overrides", [])
                
                # หา override ที่ตรงกับ armor นี้
                for override in overrides:
                    model = override.get("model", "")
                    
                    # ตรวจสอบว่า model ตรงกับ armor นี้หรือไม่
                    if namespace in model and armor_name in model:
                        print(f"✅ Found matching override: {model}")
                        
                        # หา icon texture
                        model_path = model.replace(":", "/")
                        model_json_path = f"pack/assets/{model_path}.json"
                        
                        if not os.path.exists(model_json_path):
                            print(f"⚠️ Model file not found: {model_json_path}")
                            continue
                        
                        with open(model_json_path, "r", encoding="utf-8") as f:
                            item_model = json.load(f)
                        
                        textures = item_model.get("textures", {})
                        icon_texture = textures.get("layer0") or textures.get("layer1")
                        
                        if not icon_texture:
                            print(f"⚠️ No icon texture found")
                            continue
                        
                        # Copy icon
                        if ":" in icon_texture:
                            icon_ns, icon_path = icon_texture.split(":", 1)
                        else:
                            icon_ns = namespace
                            icon_path = icon_texture
                        
                        src_icon = f"pack/assets/{icon_ns}/textures/{icon_path}.png"
                        dest_icon = f"staging/target/rp/textures/{icon_ns}/{icon_path}.png"
                        
                        os.makedirs(os.path.dirname(dest_icon), exist_ok=True)
                        
                        if os.path.exists(src_icon):
                            shutil.copy(src_icon, dest_icon)
                            print(f"🖼️ Copied icon → {dest_icon}")
                            
                            # สร้าง gmdl ID
                            armor_piece = armor_type.split("_")[1]  # helmet, chestplate, etc.
                            # หา gmdl จากไฟล์ attachable เดิม
                            gmdl = find_existing_gmdl(namespace, armor_name, armor_piece)
                            if not gmdl:
                                print(f"⚠️ Cannot find existing gmdl for {armor_name} {armor_piece}")
                                continue
                            
                            # อัปเดต item_texture.json
                            atlas_path = f"textures/{icon_ns}/{icon_path}.png"
                            update_item_texture_json(gmdl, atlas_path)
                            
                            # icons.csv
                            icons_csv = "scratch_files/icons.csv"
                            os.makedirs("scratch_files", exist_ok=True)
                            with open(icons_csv, "a", encoding="utf-8") as f:
                                f.write(f"{gmdl},{atlas_path}\n")
                            print(f"📌 Added to atlas: {gmdl}")
                            
                            # เลือก texture humanoid/leggings
                            if armor_piece == "leggings":
                                final_texture = f"textures/equipment/{namespace}_{armor_name}_leggings.png"
                            else:
                                final_texture = f"textures/equipment/{namespace}_{armor_name}_humanoid.png"
                            
                            # path base และ player
                            base_attachable = f"staging/target/rp/attachables/{namespace}/{gmdl}.json"
                            player_attachable = f"staging/target/rp/attachables/{namespace}/{gmdl}.player.json"
                            
                            # generate base attachable
                            write_equipment_base(base_attachable, gmdl, final_texture, i)
                            
                            # generate player attachable
                            write_equipment_armor(player_attachable, gmdl, final_texture, i)


                                                    
                        else:
                            print(f"⚠️ Icon not found: {src_icon}")

# ===============================
# 🧩 Auto-generate .player.json for ANY armor attachable
# ===============================
def auto_generate_player_attachables():
    print("\n" + "="*60)
    print("🛠️ Auto-generating .player.json for ARMOR ONLY")
    print("="*60)

    base_path = "staging/target/rp/attachables"

    ARMOR_KEYWORDS = ["helmet", "chestplate", "leggings", "boots"]

    # เดินทุก namespace + subfolder
    for namespace in os.listdir(base_path):
        ns_path = os.path.join(base_path, namespace)
        if not os.path.isdir(ns_path):
            continue

        # ค้นหาเฉพาะไฟล์ attachable.json ที่เป็นเกราะเท่านั้น
        attachable_files = glob.glob(ns_path + "/**/*.attachable.json", recursive=True)

        for file in attachable_files:
            lower_name = file.lower()

            # ❌ ถ้าไม่ใช่ของเกราะ → ข้าม
            if not any(key in lower_name for key in ARMOR_KEYWORDS):
                continue

            player_file = file.replace(".attachable.json", ".attachable.player.json")

            # ถ้ามีอยู่แล้วก็ข้าม
            if os.path.exists(player_file):
                print(f"⏩ Skip (already exists): {player_file}")
                continue

            # อ่าน attachable เดิม
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)["minecraft:attachable"]

            gmdl = data["description"]["identifier"].split(":")[1]

            # หา armor type จากชื่อไฟล์
            if "leggings" in lower_name:
                armor_type = "leggings"
            elif "boots" in lower_name:
                armor_type = "boots"
            elif "chest" in lower_name:
                armor_type = "chestplate"
            else:
                armor_type = "helmet"
            
            # ดึง base_name จากไฟล์ (ก่อน .gmdl_xxxxx)
            armor_name_clean = gmdl.split(".gmdl")[0]
            
            if armor_type == "leggings":
                final_texture = f"textures/equipment/{namespace}_{armor_name_clean}_leggings.png"
            else:
                final_texture = f"textures/equipment/{namespace}_{armor_name_clean}_humanoid.png"


            # JSON player attachable
            player_json = {
                "format_version": "1.10.0",
                "minecraft:attachable": {
                    "description": {
                        "identifier": f"geyser_custom:{gmdl}.player",
                        "item": {f"geyser_custom:{gmdl}": True},
                        "materials": {
                            "default": "armor",
                            "enchanted": "armor_enchanted"
                        },
                        "textures": {
                            "default": final_texture,
                            "enchanted": "textures/misc/enchanted_item_glint"
                        },
                        "geometry": {"default": f"geometry.player.armor.{armor_type}"},
                        "scripts": {"parent_setup": "variable.helmet_layer_visible = 0.0;"},
                        "render_controllers": ["controller.render.armor"]
                    }
                }
            }

            os.makedirs(os.path.dirname(player_file), exist_ok=True)
            with open(player_file, "w", encoding="utf-8") as f:
                json.dump(player_json, f, indent=4)

            print(f"🧩 Generated ARMOR ONLY: {player_file}")

def detect_armor_sources(tex_dir, namespace):
    """
    คืน mapping:
    {
       'humanoid': 'ชื่อไฟล์ต้นฉบับ',
       'leggings': 'ชื่อไฟล์ต้นฉบับ'
    }
    """
    files = glob.glob(os.path.join(tex_dir, f"{namespace}_*.png"))

    humanoid = None
    leggings = None

    for f in files:
        name = os.path.basename(f).lower()

        if "humanoid" in name:
            humanoid = os.path.basename(f)

        if "leggings" in name:
            leggings = os.path.basename(f)

    return humanoid, leggings

def fix_player_attachable_texture_paths():
    print("\n" + "="*60)
    print("🎯 Fixing .player.json textures to use REAL source textures")
    print("="*60)

    tex_dir = "staging/target/rp/textures/equipment"
    attach_path = "staging/target/rp/attachables"

    # โหลดไฟล์ texture ทั้งหมดไว้ก่อน
    all_png = glob.glob(os.path.join(tex_dir, "*.png"))
    all_png_map = {os.path.basename(f): f for f in all_png}

    # loop ทุก namespace
    for namespace in os.listdir(attach_path):
        ns_path = os.path.join(attach_path, namespace)
        if not os.path.isdir(ns_path):
            continue

        # หาชื่อ texture จริง (มีแค่ 2 ไฟล์)
        humanoid_src = None
        leggings_src = None

        for f in all_png:
            base = os.path.basename(f).lower()
            if not base.startswith(namespace.lower() + "_"):
                continue

            if "humanoid" in base:
                humanoid_src = base
            if "leggings" in base:
                leggings_src = base

        if not humanoid_src:
            continue

        # loop player.json
        for pf in glob.glob(ns_path + "/**/*.player.json", recursive=True):
            with open(pf, "r", encoding="utf-8") as f:
                data = json.load(f)

            desc = data["minecraft:attachable"]["description"]

            # ดูว่าเป็นหมวก, เสื้อ, รองเท้าหรือกางเกง
            geom = desc["geometry"]["default"]

            if "leggings" in geom:
                new_tex = f"textures/equipment/{leggings_src}"
            else:
                new_tex = f"textures/equipment/{humanoid_src}"

            old_tex = desc["textures"]["default"]
            # 🧪 ====== เพิ่มตรงนี้ ======
            # ถ้าเป็น CIT (leather armor / armor_layer) → ห้ามแตะ
            if "textures/armor_layer" in old_tex:
                continue
            # ==========================
            # ถ้าเหมือนเดิมไม่ต้องแก้
            if old_tex == new_tex:
                continue

            desc["textures"]["default"] = new_tex

            with open(pf, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print(f"🔧 Fixed {os.path.basename(pf)}")
            print(f"    {old_tex}  →  {new_tex}")

def remove_invalid_player_attachables():
    print("\n" + "="*60)
    print("🧹 Cleaning invalid .player.json (missing textures)")
    print("="*60)

    attach_path = "staging/target/rp/attachables"

    for namespace in os.listdir(attach_path):
        ns_path = os.path.join(attach_path, namespace)
        if not os.path.isdir(ns_path):
            continue

        for pf in glob.glob(ns_path + "/**/*.player.json", recursive=True):

            with open(pf, "r", encoding="utf-8") as f:
                data = json.load(f)

            desc = data["minecraft:attachable"]["description"]
            tex = desc["textures"]["default"]

            # ✅ ตรวจ path ให้ถูก (รองรับมี/ไม่มี .png)
            if tex.endswith(".png"):
                tex_path = os.path.join("staging/target/rp", tex.replace("/", os.sep))
            else:
                tex_path = os.path.join("staging/target/rp", tex.replace("/", os.sep) + ".png")

            # ✅ CIT = อย่าลบทิ้ง
            if "textures/armor_layer" in tex:

                if not os.path.exists(tex_path):
                    print(f"⚠️ WARN (CIT texture missing, NOT removed): {pf}")
                    print(f"   Missing: {tex_path}")
                else:
                    print(f"✅ OK (CIT): {pf}")

                continue

            # ❌ Equipment / Cosmetic → ลบทิ้งได้
            if not os.path.exists(tex_path):

                print(f"❌ REMOVE: {pf}")
                print(f"   Missing texture: {tex_path}")

                try:
                    os.remove(pf)
                except:
                    pass
            else:
                print(f"✅ OK: {pf}")
# ===============================
# 📥 โหลด GUI config + คัดลอก PNG ไป staging
# ===============================
def import_gui_config():
    src_gui = "pack/guis.json"
    dest_gui = "staging/guis.json"

    # path ต้นทางของโฟลเดอร์ PNG
    src_texture_folder = "pack/textures/zgui/ui/gui"
    dest_texture_folder = "staging/textures/zgui/ui/gui"

    # เอา guis.json
    if not os.path.exists(src_gui):
        print("⚠️ No guis.json found in ./pack/")
        return

    os.makedirs("staging", exist_ok=True)

    shutil.copy(src_gui, dest_gui)
    print("🎉 Imported guis.json → staging/guis.json")

    # เอา PNG ทั้งหมดใน textures/zgui/ui/gui/
    if os.path.exists(src_texture_folder):
        shutil.copytree(src_texture_folder, dest_texture_folder, dirs_exist_ok=True)
        print(f"🖼️ Imported PNGs → {dest_texture_folder}")
    else:
        print("⚠️ No PNG texture folder found:", src_texture_folder)
# ===============================
# ⚙️ Import Kaizer global config
# ===============================
def import_kaizer_config():
    src = "pack/kaizer_config.json"
    dest = "staging/kaizer_config.json"

    # สร้าง staging ถ้ายังไม่มี
    os.makedirs("staging", exist_ok=True)

    if not os.path.exists(src):
        print("⚠️ No kaizer_config.json found in ./pack/")
        return

    shutil.copy(src, dest)
    print("⚙️ Imported kaizer_config.json → staging/kaizer_config.json")


# ===================================================
# 🧩 NEXO TEXTURE SCAN + COPY (FINAL STEP)
# ===================================================
def print_nexo_summary(humanoid_files, leggings_files, matched_sets):
    missing_leggings = set(humanoid_files) - set(leggings_files)
    missing_humanoid = set(leggings_files) - set(humanoid_files)

    total_count = len(humanoid_files) + len(leggings_files)

    print("\n=================================")
    print("========== TOTAL SUMMARY ========")
    print("=================================")
    print(f"📦 Total sets/files counted: {total_count}")
    print(f"✔ Armor sets: {len(matched_sets)}")
    print(f"❌ Total missing: {len(missing_leggings) + len(missing_humanoid)}")
    print(f" - Missing leggings: {len(missing_leggings)}")
    print(f" - Missing humanoid: {len(missing_humanoid)}")
    print("=================================\n")
def process_nexo_textures():
    print("\n" + "="*60)
    print("🟣 Processing NEXO Armor Textures (Scan + Copy)")
    print("="*60)

    assets_path = r"pack/assets"

    if not os.path.exists(assets_path):
        print("❌ pack/assets not found — cannot scan.")
        return

    nexo_root = os.path.join(assets_path, "nexo")
    if not os.path.exists(nexo_root):
        print("❌ No NEXO folder inside pack/assets — skipping.")
        return

    print("✅ NEXO pack detected.\n")

    humanoid_path = os.path.join(nexo_root, "textures/entity/equipment/humanoid")
    leggings_path = os.path.join(nexo_root, "textures/entity/equipment/humanoid_leggings")

    if not os.path.exists(humanoid_path) or not os.path.exists(leggings_path):
        print("❌ Missing humanoid or humanoid_leggings folder!")
        return

    humanoid_files = {
        f.lower(): os.path.join(humanoid_path, f)
        for f in os.listdir(humanoid_path)
        if f.endswith(".png")
    }

    leggings_files = {
        f.lower(): os.path.join(leggings_path, f)
        for f in os.listdir(leggings_path)
        if f.endswith(".png")
    }

    matched_sets = set(humanoid_files) & set(leggings_files)

    print(f"🎯 Found {len(matched_sets)} matching NEXO armor sets\n")

    output_dir = "staging/target/rp/textures/layer_nexo"
    os.makedirs(output_dir, exist_ok=True)

    for name in sorted(matched_sets):
        base = name[:-4]

        src_h = humanoid_files[name]
        src_l = leggings_files[name]

        dst_h = os.path.join(output_dir, f"{base}_armor_humanoid.png")
        dst_l = os.path.join(output_dir, f"{base}_armor_leggings.png")

        shutil.copy2(src_h, dst_h)
        shutil.copy2(src_l, dst_l)

        print(f"✔ Copied: {dst_h}")
        print(f"✔ Copied: {dst_l}")

    # 📌 SUMMARY CALL (อันนี้คือที่ต้องเพิ่ม)
    print_nexo_summary(humanoid_files, leggings_files, matched_sets)

    print("\n🎉 NEXO Texture Processing Finished!\n")


# ===================================================
# 🧩 STANDARD ARMOR TEXTURE SCAN + COPY (ALL NAMESPACES EXCEPT NEXO)
# ===================================================
def process_standard_armor_textures():
    """
    สแกน armor texture ใน path ปกติ:
    assets/{namespace}/textures/entity/equipment/humanoid
    assets/{namespace}/textures/entity/equipment/humanoid_leggings
    
    สำหรับทุก namespace ที่ไม่ใช่ nexo (เพราะ nexo มี function แยกอยู่แล้ว)
    """
    print("\n" + "="*60)
    print("🔵 Processing Standard Armor Textures (All Namespaces)")
    print("="*60)

    assets_path = r"pack/assets"

    if not os.path.exists(assets_path):
        print("❌ pack/assets not found — cannot scan.")
        return

    # สแกนทุก namespace ที่มี humanoid/humanoid_leggings (ยกเว้น nexo)
    all_humanoid_files = {}
    all_leggings_files = {}
    namespaces_found = []

    for namespace in os.listdir(assets_path):
        # ข้าม nexo เพราะมี function แยกอยู่แล้ว
        if namespace.lower() == "nexo":
            continue

        ns_path = os.path.join(assets_path, namespace)
        if not os.path.isdir(ns_path):
            continue

        humanoid_path = os.path.join(ns_path, "textures/entity/equipment/humanoid")
        leggings_path = os.path.join(ns_path, "textures/entity/equipment/humanoid_leggings")

        # ถ้ามีอย่างน้อยหนึ่ง folder
        if os.path.exists(humanoid_path) or os.path.exists(leggings_path):
            namespaces_found.append(namespace)
            print(f"\n📁 Found armor textures in namespace: {namespace}")

            # Collect humanoid files
            if os.path.exists(humanoid_path):
                for f in os.listdir(humanoid_path):
                    if f.endswith(".png"):
                        key = f.lower()  # ใช้แค่ filename เป็น key
                        all_humanoid_files[key] = {
                            "path": os.path.join(humanoid_path, f),
                            "namespace": namespace,
                            "filename": f.lower()
                        }
                print(f"   ✔ humanoid: {len([f for f in os.listdir(humanoid_path) if f.endswith('.png')])} files")

            # Collect leggings files
            if os.path.exists(leggings_path):
                for f in os.listdir(leggings_path):
                    if f.endswith(".png"):
                        key = f.lower()  # ใช้แค่ filename เป็น key
                        all_leggings_files[key] = {
                            "path": os.path.join(leggings_path, f),
                            "namespace": namespace,
                            "filename": f.lower()
                        }
                print(f"   ✔ humanoid_leggings: {len([f for f in os.listdir(leggings_path) if f.endswith('.png')])} files")

    if not namespaces_found:
        print("ℹ️ No standard armor textures found in any namespace (excluding nexo).")
        return

    print(f"\n� Total namespaces with armor textures: {len(namespaces_found)}")
    print(f"   Namespaces: {', '.join(namespaces_found)}")

    # หา matched sets (ที่มีทั้ง humanoid และ leggings)
    matched_sets = set(all_humanoid_files.keys()) & set(all_leggings_files.keys())

    print(f"\n🎯 Found {len(matched_sets)} matching armor sets (both humanoid + leggings)\n")

    output_dir = "staging/target/rp/textures/layer_armor"
    os.makedirs(output_dir, exist_ok=True)

    # Copy matched sets
    for key in sorted(matched_sets):
        h_info = all_humanoid_files[key]
        l_info = all_leggings_files[key]
        base = h_info["filename"][:-4]  # remove .png

        src_h = h_info["path"]
        src_l = l_info["path"]

        # ใช้ชื่อไฟล์เดิม ไม่มี namespace prefix
        dst_h = os.path.join(output_dir, f"{base}_armor_humanoid.png")
        dst_l = os.path.join(output_dir, f"{base}_armor_leggings.png")

        shutil.copy2(src_h, dst_h)
        shutil.copy2(src_l, dst_l)

        print(f"✔ Copied: {dst_h}")
        print(f"✔ Copied: {dst_l}")

    # Copy humanoid-only files (ไม่มี leggings คู่)
    humanoid_only = set(all_humanoid_files.keys()) - set(all_leggings_files.keys())
    if humanoid_only:
        print(f"\n📦 Copying {len(humanoid_only)} humanoid-only files (no matching leggings):")
        for key in sorted(humanoid_only):
            h_info = all_humanoid_files[key]
            base = h_info["filename"][:-4]

            src_h = h_info["path"]
            dst_h = os.path.join(output_dir, f"{base}_armor_humanoid.png")

            shutil.copy2(src_h, dst_h)
            print(f"✔ Copied (humanoid only): {dst_h}")

    # Copy leggings-only files (ไม่มี humanoid คู่)
    leggings_only = set(all_leggings_files.keys()) - set(all_humanoid_files.keys())
    if leggings_only:
        print(f"\n📦 Copying {len(leggings_only)} leggings-only files (no matching humanoid):")
        for key in sorted(leggings_only):
            l_info = all_leggings_files[key]
            base = l_info["filename"][:-4]

            src_l = l_info["path"]
            dst_l = os.path.join(output_dir, f"{base}_armor_leggings.png")

            shutil.copy2(src_l, dst_l)
            print(f"✔ Copied (leggings only): {dst_l}")

    # 📌 SUMMARY
    print("\n" + "="*60)
    print("========== STANDARD ARMOR TEXTURE SUMMARY ==========")
    print("="*60)
    print(f"📁 Namespaces scanned: {len(namespaces_found)}")
    print(f"📦 Total humanoid files: {len(all_humanoid_files)}")
    print(f"📦 Total leggings files: {len(all_leggings_files)}")
    print(f"✔ Complete armor sets: {len(matched_sets)}")
    print(f"⚠ Humanoid only: {len(humanoid_only)}")
    print(f"⚠ Leggings only: {len(leggings_only)}")
    print("="*60)

    print("\n🎉 Standard Armor Texture Processing Finished!\n")


# ===============================
# �🚀 MAIN START
# ===============================
geyser_mappings_file = "staging/target/geyser_mappings.json"
if os.path.exists(geyser_mappings_file):
    remove_duplicates_with_custom_model_data(geyser_mappings_file)


process_leather_armor() # ประมวลผล Leather Armor
process_equipment_armor() # ประมวลผล Equipment Armor (Netherite, etc.)
auto_generate_player_attachables()
fix_player_attachable_texture_paths()
remove_invalid_player_attachables()
import_gui_config()
import_kaizer_config()
process_nexo_textures()
process_standard_armor_textures()  # สแกน armor texture ทุก namespace (ยกเว้น nexo)
print("\n" + "="*60)
print("✅ All armor processing complete!")
print("="*60)
