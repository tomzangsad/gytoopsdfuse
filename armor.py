import os
import json
import shutil
import glob
from jproperties import Properties



def load_gmdl_mapping():
    mapping_file = "staging/target/geyser_mappings.json"
    if not os.path.exists(mapping_file):
        print("❌ geyser_mappings.json not found")
        return {}

    with open(mapping_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cmd_to_gmdl = {}

    for item, entries in data.items():
        for e in entries:
            if "custom_model_data" in e and "name" in e:
                cmd_to_gmdl[str(e["custom_model_data"])] = e["name"]

    print(f"✅ Loaded gmdl mapping: {len(cmd_to_gmdl)} items")
    return cmd_to_gmdl

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

                # ===== PATCH: gmdl จาก mapping =====
                cmd = override.get("predicate", {}).get("custom_model_data")
                if not cmd:
                    print("⚠️ No custom_model_data for leather item")
                    continue

                gmdl = CMD_TO_GMDL.get(str(cmd))
                if not gmdl:
                    print(f"❌ gmdl not found for CMD {cmd}")
                    continue

                # ✅ base attachable path
                base_attach = f"staging/target/rp/attachables/{namespace}/{gmdl}.json"

                # ✅ ถ้ายังไม่มี base → สร้าง
                if not os.path.exists(base_attach):
                    write_equipment_armor(base_attach, gmdl, f"textures/armor_layer/{layer}", i)

                # ✅ player attachable
                pfile = f"staging/target/rp/attachables/{namespace}/{gmdl}.player.json"

                # Add icon → icons.csv
                atlas_texture_path = f"textures/{namespace}/{icon_texture}.png"

                os.makedirs("scratch_files", exist_ok=True)
                with open("scratch_files/icons.csv", "a", encoding="utf-8") as f:
                    f.write(f"{gmdl},{atlas_texture_path}\n")

                print(f"📌 Added icon to atlas: {gmdl} → {atlas_texture_path}")

                # อัปเดต item_texture.json
                update_item_texture_json(gmdl, atlas_texture_path)

                # Generate player attachable
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
    ⚠ deprecated
    """
    return None
    
def detect_equipment_texture_root(namespace):
    """
    ตรวจว่ามาจาก:
    - IA overlay
    - nexo
    คืน path root ของ textures
    """

    ia_path = f"pack/ia_overlay_1_21_2_plus/assets/{namespace}/textures/entity/equipment"
    nexo_path = f"pack/assets/{namespace}/textures/entity/equipment"

    if os.path.exists(ia_path):
        print(f"✅ Detected IA overlay equipment path: {ia_path}")
        return ia_path

    if os.path.exists(nexo_path):
        print(f"✅ Detected NEXO equipment path: {nexo_path}")
        return nexo_path

    print(f"❌ No equipment texture root found for {namespace}")
    return None

# ===============================
# 🛡️ ประมวลผล Netherite/Equipment Armor
# ===============================
def process_equipment_armor():
    print("\n" + "="*60)
    print("⚔️ FINAL Equipment Armor Processor (IA + NEXO)")
    print("="*60)

    ia_root = "pack/ia_overlay_1_21_2_plus/assets"
    nexo_root = "pack/assets"

    namespaces = set()

    # ===== scan IA =====
    if os.path.exists(ia_root):
        for ns in os.listdir(ia_root):
            if os.path.exists(os.path.join(ia_root, ns, "models", "equipment")):
                namespaces.add(ns)

    # ===== scan NEXO =====
    if os.path.exists(nexo_root):
        for ns in os.listdir(nexo_root):
            if os.path.exists(os.path.join(nexo_root, ns, "models", "equipment")):
                namespaces.add(ns)

    namespaces = list(namespaces)
    print(f"✅ Namespaces: {namespaces}")

    if not namespaces:
        print("❌ No equipment models found")
        return

    # ====================
    # LOOP namespace
    # ====================
    for namespace in namespaces:

        # detect source pack
        if os.path.exists(f"{ia_root}/{namespace}"):
            root = f"{ia_root}/{namespace}"
        elif os.path.exists(f"{nexo_root}/{namespace}"):
            root = f"{nexo_root}/{namespace}"
        else:
            continue

        models_dir = os.path.join(root, "models", "equipment")
        if not os.path.exists(models_dir):
            continue

        print(f"\n📦 {namespace}")

        # ====================
        # LOOP armor model
        # ====================
        for model_file in glob.glob(os.path.join(models_dir, "*.json")):
            armor_name = os.path.basename(model_file).replace(".json", "")
            print(f"\n🛡️ {namespace}:{armor_name}")

            try:
                with open(model_file, "r", encoding="utf-8") as f:
                    model = json.load(f)
            except:
                print("❌ Model load error")
                continue

            # ====================
            # READ textures
            # ====================
            layers = model.get("layers", {})
            humanoid = None
            leggings = None
            
            if isinstance(layers, dict):
                h = layers.get("humanoid")
                if isinstance(h, list) and h and isinstance(h[0], dict):
                    humanoid = h[0].get("texture")
                elif isinstance(h, dict):
                    humanoid = h.get("texture")

                l = layers.get("humanoid_leggings")
                if isinstance(l, list) and l and isinstance(l[0], dict):
                    leggings = l[0].get("texture")
                elif isinstance(l, dict):
                    leggings = l.get("texture")

            elif isinstance(layers, list):
                for entry in layers:
                    if not isinstance(entry, dict):
                        continue
                    if entry.get("type") == "humanoid":
                        humanoid = entry.get("texture")
                    elif entry.get("type") in ("humanoid_leggings", "leggings"):
                        leggings = entry.get("texture")

            # ====================
            # COPY textures
            # ====================
            tex_root = detect_equipment_texture_root(namespace)
            if not tex_root:
                continue

            def copy(tex, folder):
                if not tex:
                    return None
                if ":" not in tex:
                    return None

                name = tex.split(":")[1] + ".png"
                src = os.path.join(tex_root, folder, name)
                dst = f"staging/target/rp/textures/equipment/{namespace}_{armor_name}_{folder}.png"
                os.makedirs(os.path.dirname(dst), exist_ok=True)

                if os.path.exists(src):
                    shutil.copy(src, dst)
                    print(f"🧩 Copied {dst}")
                    return dst
                return None

            humanoid_dst = copy(humanoid, "humanoid")
            leggings_dst = copy(leggings, "humanoid_leggings") if leggings else humanoid_dst

            if not humanoid_dst:
                print("❌ Skip armor, humanoid texture missing")
                continue

            # ====================
            # APPLY to items
            # ====================
            armor_map = [
                ("netherite_helmet", "helmet"),
                ("netherite_chestplate", "chestplate"),
                ("netherite_leggings", "leggings"),
                ("netherite_boots", "boots")
            ]

            for i, (item_name, piece) in enumerate(armor_map):

                item_json = f"pack/assets/minecraft/models/item/{item_name}.json"
                if not os.path.exists(item_json):
                    continue

                with open(item_json, "r", encoding="utf-8") as f:
                    item = json.load(f)

                for o in item.get("overrides", []):
                    model_ref = o.get("model", "")

                    if namespace not in model_ref or armor_name not in model_ref:
                        continue

                    print(f"✅ Match: {model_ref}")

                    model_file = f"pack/assets/{model_ref.replace(':','/')}.json"
                    if not os.path.exists(model_file):
                        continue

                    with open(model_file, "r", encoding="utf-8") as f:
                        m = json.load(f)

                    icon = m.get("textures", {}).get("layer0") or m.get("textures", {}).get("layer1")
                    if not icon:
                        continue

                    icon_ns, icon_path = icon.split(":")
                    src = f"pack/assets/{icon_ns}/textures/{icon_path}.png"
                    dst = f"staging/target/rp/textures/{icon_ns}/{icon_path}.png"
                    os.makedirs(os.path.dirname(dst), exist_ok=True)

                    if os.path.exists(src):
                        shutil.copy(src, dst)

                    # ===== PATCH: gmdl จาก mapping =====
                    cmd = o.get("predicate", {}).get("custom_model_data")
                    if not cmd:
                        continue

                    gmdl = CMD_TO_GMDL.get(str(cmd))
                    if not gmdl:
                        print(f"❌ gmdl not found for CMD {cmd}")
                        continue

                    atlas = f"textures/{icon_ns}/{icon_path}.png"
                    update_item_texture_json(gmdl, atlas)

                    os.makedirs("scratch_files", exist_ok=True)
                    with open("scratch_files/icons.csv", "a", encoding="utf-8") as f:
                        f.write(f"{gmdl},{atlas}\n")

                    # ----- texture path -----
                    if piece == "leggings":
                        final = f"textures/equipment/{namespace}_{armor_name}_humanoid_leggings.png"
                    else:
                        final = f"textures/equipment/{namespace}_{armor_name}_humanoid.png"

                    write_equipment_base(
                        f"staging/target/rp/attachables/{namespace}/{gmdl}.json",
                        gmdl, final, i
                    )

                    write_equipment_armor(
                        f"staging/target/rp/attachables/{namespace}/{gmdl}.player.json",
                        gmdl, final, i
                    )


# ===============================
# 🧩 Auto-generate .player.json for ANY armor attachable
# ===============================
def auto_generate_player_attachables():
    print("\n" + "="*60)
    print("🛠️ Auto-generating .player.json for ARMOR ONLY")
    print("="*60)

    base_path = "staging/target/rp/attachables"
    ARMOR_KEYWORDS = ["helmet", "chestplate", "leggings", "boots"]

    for namespace in os.listdir(base_path):
        ns_path = os.path.join(base_path, namespace)
        if not os.path.isdir(ns_path):
            continue

        attachable_files = glob.glob(ns_path + "/**/*.attachable.json", recursive=True)

        for file in attachable_files:
            lower = file.lower()
            if not any(k in lower for k in ARMOR_KEYWORDS):
                continue

            player_file = file.replace(".attachable.json", ".attachable.player.json")
            if os.path.exists(player_file):
                continue

            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)["minecraft:attachable"]

            gmdl = data["description"]["identifier"].split(":")[1]

            if "leggings" in lower:
                armor_type = "leggings"
            elif "boots" in lower:
                armor_type = "boots"
            elif "chest" in lower:
                armor_type = "chestplate"
            else:
                armor_type = "helmet"

            name_clean = gmdl.split(".gmdl")[0]

            tex = f"textures/equipment/{namespace}_{name_clean}_{'humanoid_leggings' if armor_type=='leggings' else 'humanoid'}.png"

            player_json = {
                "format_version": "1.10.0",
                "minecraft:attachable": {
                    "description": {
                        "identifier": f"geyser_custom:{gmdl}.player",
                        "item": {f"geyser_custom:{gmdl}": "query.owner_identifier == 'minecraft:player'"},
                        "materials": {"default": "armor", "enchanted": "armor_enchanted"},
                        "textures": {"default": tex, "enchanted": "textures/misc/enchanted_item_glint"},
                        "geometry": {"default": f"geometry.player.armor.{armor_type}"},
                        "scripts": {"parent_setup": "variable.helmet_layer_visible = 0.0;"},
                        "render_controllers": ["controller.render.armor"]
                    }
                }
            }

            os.makedirs(os.path.dirname(player_file), exist_ok=True)
            with open(player_file, "w", encoding="utf-8") as f:
                json.dump(player_json, f, indent=4)

            print(f"🧩 Generated {player_file}")


def fix_player_attachable_texture_paths():
    print("\n" + "="*60)
    print("🎯 Fixing .player.json textures")
    print("="*60)

    tex_dir = "staging/target/rp/textures/equipment"
    attach_path = "staging/target/rp/attachables"

    all_png = [os.path.basename(p) for p in glob.glob(os.path.join(tex_dir, "*.png"))]

    for namespace in os.listdir(attach_path):
        ns_path = os.path.join(attach_path, namespace)
        if not os.path.isdir(ns_path):
            continue

        humanoid = None
        leggings = None

        for n in all_png:
            if not n.startswith(namespace + "_"):
                continue
            if "humanoid_leggings" in n:
                leggings = n
            elif "humanoid" in n:
                humanoid = n

        if not humanoid:
            continue

        for file in glob.glob(ns_path + "/**/*.player.json", recursive=True):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            geom = data["minecraft:attachable"]["description"]["geometry"]["default"]

            new = f"textures/equipment/{leggings if 'leggings' in geom else humanoid}"
            old = data["minecraft:attachable"]["description"]["textures"]["default"]

            if old != new:
                data["minecraft:attachable"]["description"]["textures"]["default"] = new
                with open(file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                print(f"🔧 Fixed {file}")


def remove_invalid_player_attachables():
    print("\n" + "="*60)
    print("🧹 Cleaning invalid player attachables")
    print("="*60)

    attach_path = "staging/target/rp/attachables"

    for namespace in os.listdir(attach_path):
        ns_path = os.path.join(attach_path, namespace)
        if not os.path.isdir(ns_path):
            continue

        for pf in glob.glob(ns_path + "/**/*.player.json", recursive=True):
            with open(pf, "r", encoding="utf-8") as f:
                data = json.load(f)

            tex = data["minecraft:attachable"]["description"]["textures"]["default"]
            tex_path = os.path.join("staging/target/rp", tex.replace("/", os.sep))
            if not tex_path.endswith(".png"):
                tex_path += ".png"

            if "armor_layer" in tex:
                continue

            if not os.path.exists(tex_path):
                print(f"❌ REMOVE {pf}")
                os.remove(pf)


# ===============================
# 🚀 MAIN START
# ===============================
geyser_mappings_file = "staging/target/geyser_mappings.json"
if os.path.exists(geyser_mappings_file):
    remove_duplicates_with_custom_model_data(geyser_mappings_file)

CMD_TO_GMDL = load_gmdl_mapping()

process_leather_armor()
process_equipment_armor()
auto_generate_player_attachables()
fix_player_attachable_texture_paths()
remove_invalid_player_attachables()

print("\n" + "="*60)
print("✅ All armor processing complete!")
print("="*60)
