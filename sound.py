import json, glob, os, shutil

def copy_sound(name):
    """copy sound file from correct namespace folder"""
    namespace, rel = name.split(":")
    src = f"pack/assets/{namespace}/sounds/{rel}.ogg"
    dst = f"staging/target/rp/sounds/{rel}.ogg"

    if not os.path.exists(src):
        print(f"⚠ Missing sound file: {src}")
        return None

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)

    # BEDROCK USES: sounds/<rel>
    return f"sounds/{rel}"

# ---------------------------------------------------------
# Load all sounds.json
# ---------------------------------------------------------
files = glob.glob("pack/assets/**/sounds.json")
print(f"Sounds Files: {files}")

# Prepare bedrock sound_definitions
os.makedirs("staging/target/rp/sounds", exist_ok=True)
sound_defs_path = "staging/target/rp/sounds/sound_definitions.json"

sound_defs = {
    "format_version": "1.14.0",
    "sound_definitions": {}
}

# ---------------------------------------------------------
# Convert every sounds.json
# ---------------------------------------------------------
for file in files:
    with open(file, "r") as f:
        data = json.load(f)

    namespace = file.split(os.sep)[2]  # pack/assets/<namespace>/sounds.json
    print("Processing namespace:", namespace)

    for name, info in data.items():

        full_id = f"{namespace}:{name}"
        sound_defs["sound_definitions"][full_id] = {}

        # category
        sound_defs["sound_definitions"][full_id]["category"] = info.get("category", "neutral")

        listsound = []

        for sound in info["sounds"]:
            # dict: {"name": "fluffyworld:xsound/bling"}
            if isinstance(sound, dict):
                sname = sound["name"]
                out = copy_sound(sname)
                if out:
                    sound["name"] = out
                    listsound.append(sound)

            # string: "fluffyworld:xsound/bling"
            else:
                out = copy_sound(sound)
                if out:
                    listsound.append(out)

        sound_defs["sound_definitions"][full_id]["sounds"] = listsound

# ---------------------------------------------------------
# Save final sound_definitions.json
# ---------------------------------------------------------
with open(sound_defs_path, "w") as f:
    json.dump(sound_defs, f, indent=2)

print("✔ Done converting sounds!")
