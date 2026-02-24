"""
shorten_paths.py  –  Shorten file paths in a Bedrock RP so all paths stay
                     below the 80-character limit that Geyser enforces.

Usage (called automatically from converter.sh):
    python shorten_paths.py <target_rp_dir> [max_path_len]

Algorithm:
  1. Walk <target_rp_dir> and collect every relative path that is >= max_path_len.
  2. From those paths, extract individual directory/filename components that are:
       - NOT a vanilla-reserved word (PROTECTED set)
       - Long enough to be worth abbreviating (>= MIN_COMP_LEN chars)
  3. Build a deterministic mapping  long_name -> short_name  (vX0, vX1, …).
  4. Do a bottom-up walk of the directory tree:
       a. Update contents of .json / .properties / .mcmeta files.
       b. Rename files.
       c. Rename directories.
  5. Report how many paths are still too long after shortening.
"""

import os
import sys
import re

# ─── Constants ────────────────────────────────────────────────────────────────

MAX_PATH_LEN  = 80   # Geyser warning threshold
MIN_COMP_LEN  = 8    # Only shorten components >= this length

# Words that must never be renamed – vanilla MC / Bedrock structure words
PROTECTED = {
    # Bedrock / Java pack structure
    "assets", "minecraft", "models", "textures", "item", "items",
    "block", "blocks", "optifine", "cit", "mcpatcher", "sounds",
    "font", "lang", "texts", "particles", "properties", "json",
    "png", "mcmeta", "ogg", "gui", "ui", "entity", "entities",
    "armor", "armors", "environment", "misc", "mob_effect",
    "painting", "missingno", "animation", "animations",
    "texture", "model", "attachables", "geometry",
    # Vanilla tool / armor base names
    "diamond_sword", "diamond_pickaxe", "diamond_shovel",
    "diamond_axe", "diamond_hoe",
    "golden_sword",  "golden_pickaxe",  "golden_shovel",
    "golden_axe",    "golden_hoe",
    "iron_sword",    "iron_pickaxe",    "iron_shovel",
    "iron_axe",      "iron_hoe",
    "wooden_sword",  "wooden_pickaxe",  "wooden_shovel",
    "wooden_axe",    "wooden_hoe",
    "stone_sword",   "stone_pickaxe",   "stone_shovel",
    "stone_axe",     "stone_hoe",
    "netherite_sword","netherite_pickaxe","netherite_shovel",
    "netherite_axe", "netherite_hoe",
    "leather_helmet","leather_chestplate","leather_leggings","leather_boots",
    "chainmail_helmet","chainmail_chestplate","chainmail_leggings","chainmail_boots",
    "iron_helmet",   "iron_chestplate",  "iron_leggings",   "iron_boots",
    "diamond_helmet","diamond_chestplate","diamond_leggings","diamond_boots",
    "golden_helmet", "golden_chestplate","golden_leggings", "golden_boots",
    "netherite_helmet","netherite_chestplate","netherite_leggings","netherite_boots",
    "fishing_rod", "crossbow", "shield",
    "carrot_on_a_stick", "warped_fungus_on_a_stick",
    "leather_horse_armor","iron_horse_armor",
    "golden_horse_armor", "diamond_horse_armor",
    "trident", "elytra", "shears", "flint_and_steel",
    "bow", "apple", "arrow",
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def is_protected(name: str) -> bool:
    """Return True if the name (without extension) is in the protected set."""
    base = os.path.splitext(name)[0].lower()
    return base in PROTECTED or name.lower() in PROTECTED


def collect_long_components(target_dir: str, max_len: int, min_comp: int) -> list[str]:
    """
    Find all path components that appear in paths exceeding max_len characters
    and are themselves >= min_comp characters and not protected.
    Returns a list sorted longest-first (so longer names are replaced first,
    avoiding accidental partial substitutions).
    """
    cands: set[str] = set()

    for root, dirs, files in os.walk(target_dir):
        for fname in files:
            full    = os.path.join(root, fname)
            rel     = os.path.relpath(full, target_dir).replace("\\", "/")
            if len(rel) < max_len:
                continue
            parts = re.split(r"[/\\]", rel)
            for i, part in enumerate(parts):
                is_last = (i == len(parts) - 1)
                component = os.path.splitext(part)[0] if is_last else part
                if (
                    len(component) >= min_comp
                    and not component.isdigit()
                    and not is_protected(component)
                ):
                    cands.add(component)

    return sorted(cands, key=lambda x: (-len(x), x))


def apply_mapping(text: str, mapping: dict[str, str]) -> str:
    for old, new in mapping.items():
        text = text.replace(old, new)
    return text


def patch_file_contents(filepath: str, mapping: dict[str, str]) -> bool:
    """Update string references inside text-based files (.json/.properties/.mcmeta)."""
    if not filepath.endswith((".json", ".properties", ".mcmeta")):
        return False
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            original = fh.read()
    except (UnicodeDecodeError, OSError):
        return False

    updated = apply_mapping(original, mapping)
    if updated != original:
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(updated)
        return True
    return False


def rename_tree(target_dir: str, mapping: dict[str, str]):
    """
    Bottom-up walk: patch file contents first, then rename files, then dirs.
    Bottom-up order ensures parent directories are renamed after their children.
    """
    for root, dirs, files in os.walk(target_dir, topdown=False):
        # 1. Patch + rename files
        for fname in files:
            fpath = os.path.join(root, fname)
            patch_file_contents(fpath, mapping)

            new_fname = apply_mapping(fname, mapping)
            if new_fname != fname:
                os.rename(fpath, os.path.join(root, new_fname))

        # 2. Rename directories
        for dname in dirs:
            dpath = os.path.join(root, dname)
            new_dname = apply_mapping(dname, mapping)
            if new_dname != dname:
                new_dpath = os.path.join(root, new_dname)
                if os.path.exists(dpath):          # may have been renamed already
                    os.rename(dpath, new_dpath)


def count_long_paths(target_dir: str, max_len: int) -> list[str]:
    long = []
    for root, dirs, files in os.walk(target_dir):
        for fname in files:
            full = os.path.join(root, fname)
            rel  = os.path.relpath(full, target_dir).replace("\\", "/")
            if len(rel) >= max_len:
                long.append(rel)
    return long


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    target_dir  = sys.argv[1] if len(sys.argv) > 1 else "staging/target/rp"
    max_path_len = int(sys.argv[2]) if len(sys.argv) > 2 else MAX_PATH_LEN

    if not os.path.exists(target_dir):
        print(f"[shorten_paths] Target directory '{target_dir}' not found – skipping.")
        sys.exit(0)

    print(f"[shorten_paths] Scanning '{target_dir}' for paths >= {max_path_len} chars...")

    long_before = count_long_paths(target_dir, max_path_len)
    if not long_before:
        print("[shorten_paths] No paths exceed the limit. Nothing to do.")
        sys.exit(0)

    print(f"[shorten_paths] Found {len(long_before)} path(s) that exceed {max_path_len} chars.")

    candidates = collect_long_components(target_dir, max_path_len, MIN_COMP_LEN)

    if not candidates:
        print("[shorten_paths] No shortenable components found (all components are protected or short).")
        sys.exit(0)

    # Map long component -> short token  e.g.  mimix_phantom -> vX0
    mapping = {comp: f"vX{i}" for i, comp in enumerate(candidates)}

    print(f"[shorten_paths] Planned {len(mapping)} replacement(s):")
    for old, new in list(mapping.items())[:30]:
        print(f"  {old!r:40s} -> {new!r}")
    if len(mapping) > 30:
        print(f"  ... and {len(mapping) - 30} more")

    print("\n[shorten_paths] Applying renames...")
    rename_tree(target_dir, mapping)

    long_after = count_long_paths(target_dir, max_path_len)
    print(f"[shorten_paths] Done. Paths still >= {max_path_len} chars: {len(long_after)}")
    if long_after:
        print("[shorten_paths] Remaining long paths (may need further manual shortening):")
        for p in long_after[:20]:
            print(f"  {p}  ({len(p)} chars)")


if __name__ == "__main__":
    main()
