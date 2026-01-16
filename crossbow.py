import os
import json
import glob
from crossbow_util import Crossbow_Util

if os.path.exists("pack/assets/minecraft/models/item/crossbow.json"):
    with open("pack/assets/minecraft/models/item/crossbow.json") as f:
        data = json.load(f)
        predicate = [d["predicate"] for d in data["overrides"]]
        model = [d["model"] for d in data["overrides"]]
    for m, p in zip(model, predicate):
        if m in ["item/crossbow", "item/crossbow_pulling_0", "item/crossbow_pulling_1", "item/crossbow_pulling_2", "item/crossbow_arrow", "item/crossbow_firework"] or not "custom_model_data" in p:
            continue
        i = 0
        try:
            if p.get("pulling") == 1:
                # Crossbow pulling states
                pull = p.get("pull", 0)
                if pull <= 0.58:
                    i = 1
                elif pull <= 1.0:
                    i = 2
            elif p.get("charged") == 1:
                # Crossbow is charged
                if p.get("firework") == 1:
                    i = 4  # crossbow with firework
                else:
                    i = 3  # crossbow with arrow
        except:
            pass
        fpath = (f"cache/crossbow/{p['custom_model_data']}.json")
        if not os.path.exists(fpath):
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, "w") as f:
                f.write("{}")
        with open(fpath, "r") as f:
            data = json.load(f)
        with open(fpath, "w") as f:
            if "check" in data:
                data["check"] = data["check"] + 1
            else:
                data["check"] = 1
            data[f'texture_{i}'] = m
            json.dump(data, f, indent=2)

files = glob.glob("cache/crossbow/*.json")
Crossbow_Util.animation()
Crossbow_Util.rendercontrollers()
gmdllist = []
for file in files:
    try:
        with open(file, "r") as f:
            data = json.load(f)
        if data["check"] == 5:  # Crossbow has 5 states: standby, pulling_0, pulling_1, arrow, firework
            textures = []
            geometry = []
            for i in range(5):
                namespace = data[f"texture_{i}"].split(":")[0]
                path = data[f"texture_{i}"].split(":")[1]
                files = glob.glob(f"staging/target/rp/attachables/{namespace}/{path}*.json")
                for fa in files:
                    if f"{path.split('/')[-1]}." in fa:
                        break
                with open(fa, "r") as f:
                    dataA = json.load(f)
                    f.close()
                    textures.append(dataA["minecraft:attachable"]["description"]["textures"]["default"])
                    is2Dcrossbow = Crossbow_Util.is2Dcrossbow(glob.glob(f"staging/target/rp/models/blocks/{namespace}/{path}.json")[0])
                    if is2Dcrossbow:
                        if i == 0: geometry.append("geometry.crossbow_standby")
                        elif i == 1: geometry.append("geometry.crossbow_pulling_0")
                        elif i == 2: geometry.append("geometry.crossbow_pulling_1")
                        elif i == 3: geometry.append("geometry.crossbow_arrow")
                        elif i == 4: geometry.append("geometry.crossbow_firework")
                    else: geometry.append(dataA["minecraft:attachable"]["description"]["geometry"]["default"])
                    if i == 0:
                        if is2Dcrossbow:
                            animate = [{"wield":"c.is_first_person"},{"third_person":"!c.is_first_person"},{"wield_first_person_pull":"query.main_hand_item_use_duration > 0.0f && c.is_first_person"}]
                            pre_animation = ["v.charge_amount = math.clamp((q.main_hand_item_max_duration - (q.main_hand_item_use_duration - q.frame_alpha + 1.0)) / 25.0, 0.0, 1.0f);","v.total_frames = 4;","v.step = v.total_frames / 60;","v.frame = query.is_using_item ? math.clamp((v.frame ?? 0) + v.step, 1, v.total_frames) : (q.is_item_name_any('slot.weapon.mainhand', 'minecraft:crossbow') && v.is_charged ? 3 : 0);","v.is_charged = q.is_item_name_any('slot.weapon.mainhand', 'minecraft:crossbow') && !query.is_using_item && v.frame >= 3;"]
                        else:
                            animate = [{"thirdperson_main_hand":"v.main_hand && !c.is_first_person"},{"thirdperson_off_hand":"v.off_hand && !c.is_first_person"},{"thirdperson_head":"v.head && !c.is_first_person"},{"firstperson_main_hand":"v.main_hand && c.is_first_person"},{"firstperson_off_hand":"v.off_hand && c.is_first_person"},{"firstperson_head":"c.is_first_person && v.head"}]
                            pre_animation = ["v.charge_amount = math.clamp((q.main_hand_item_max_duration - (q.main_hand_item_use_duration - q.frame_alpha + 1.0)) / 25.0, 0.0, 1.0f);","v.total_frames = 4;","v.step = v.total_frames / 60;","v.frame = query.is_using_item ? math.clamp((v.frame ?? 0) + v.step, 1, v.total_frames) : (q.is_item_name_any('slot.weapon.mainhand', 'minecraft:crossbow') && v.is_charged ? 3 : 0);","v.is_charged = q.is_item_name_any('slot.weapon.mainhand', 'minecraft:crossbow') && !query.is_using_item && v.frame >= 3;","v.main_hand = c.item_slot == 'main_hand';","v.off_hand = c.item_slot == 'off_hand';","v.head = c.item_slot == 'head';"]
                        mfile = fa
                        mdefault = dataA["minecraft:attachable"]["description"]["materials"]["default"]
                        menchanted = dataA["minecraft:attachable"]["description"]["materials"]["enchanted"]
                        gmdl = dataA["minecraft:attachable"]["description"]["identifier"].split(":")[1]
                        animations = dataA["minecraft:attachable"]["description"]["animations"]
                        animations["wield"] = "animation.player.crossbow_custom.first_person"
                        animations["third_person"] = "animation.player.crossbow_custom"
                        animations["wield_first_person_pull"] = "animation.crossbow.wield_first_person_pull"
                        gmdllist.append(f"geyser_custom:{gmdl}")
                        Crossbow_Util.item_texture(gmdl, textures[0])
                    else:
                        os.remove(fa)
            Crossbow_Util.write(mfile, gmdl, textures, geometry, mdefault, menchanted, animations, animate, pre_animation)
    except Exception as e:
        print(e)
Crossbow_Util.acontroller(gmdllist)
