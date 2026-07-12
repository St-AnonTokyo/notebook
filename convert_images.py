"""Batch convert PNG/JPG images to WebP and update markdown references.

Handles three cases per image:
  1. No WebP exists yet  -> convert, update .md, delete original
  2. WebP already exists -> skip conversion, but still update .md and delete original
  3. WebP missing        -> convert
"""
import os
import re
from pathlib import Path
from PIL import Image

DOCS_DIR = Path(__file__).parent / "docs"
EXTENSIONS = {".png", ".jpg", ".jpeg"}
QUALITY = 85

# Collect every png/jpg that has (or will have) a webp counterpart
pairs = []          # list of (original_path, webp_path)
newly_converted = 0

for img_path in sorted(DOCS_DIR.rglob("*")):
    if not img_path.is_file():
        continue
    if img_path.suffix.lower() not in EXTENSIONS:
        continue
    # Skip theme assets directly in docs/img/ (logo, favicon)
    rel_parts = img_path.relative_to(DOCS_DIR).parts
    if len(rel_parts) >= 2 and rel_parts[0] == "img":
        continue

    webp_path = img_path.with_suffix(".webp")

    if webp_path.exists():
        print(f"WebP exists, will update refs & delete original: {img_path.relative_to(DOCS_DIR)}")
    else:
        print(f"Converting: {img_path.relative_to(DOCS_DIR)}", end=" ... ")
        try:
            img = Image.open(img_path)
            if img.mode in ("RGBA", "LA", "P"):
                img.save(webp_path, "WEBP", quality=QUALITY, method=6)
            else:
                img = img.convert("RGB")
                img.save(webp_path, "WEBP", quality=QUALITY, method=6)
            old_kb = img_path.stat().st_size / 1024
            new_kb = webp_path.stat().st_size / 1024
            ratio = (1 - new_kb / old_kb) * 100
            print(f"{old_kb:.0f}KB -> {new_kb:.0f}KB ({ratio:.0f}% smaller)")
            newly_converted += 1
        except Exception as e:
            print(f"ERROR: {e}")
            continue

    pairs.append((img_path, webp_path))

# Update all .md files: replace every .png/.jpg/.jpeg ref with .webp
print(f"\nUpdating markdown references...")
updated_files = 0
for md_path in DOCS_DIR.rglob("*.md"):
    content = md_path.read_text(encoding="utf-8")
    new_content = content
    for old_path, new_path in pairs:
        # Relative path replacement: img/foo.png -> img/foo.webp
        old_rel = os.path.relpath(old_path, md_path.parent).replace("\\", "/")
        new_rel = os.path.relpath(new_path, md_path.parent).replace("\\", "/")
        new_content = new_content.replace(old_rel, new_rel)
        # Fallback: any remaining stem.png/jpg/jpeg -> stem.webp
        new_content = re.sub(
            re.escape(old_path.stem) + r"\.(png|jpg|jpeg)",
            new_path.stem + ".webp",
            new_content,
        )
    if new_content != content:
        md_path.write_text(new_content, encoding="utf-8")
        updated_files += 1
        print(f"  Updated: {md_path.relative_to(DOCS_DIR)}")

# Delete all original files that now have a webp counterpart
print(f"\nDeleting original files...")
deleted = 0
for old_path, webp_path in pairs:
    if old_path.exists():
        old_path.unlink()
        deleted += 1
        print(f"  Deleted: {old_path.relative_to(DOCS_DIR)}")

print(f"\nDone! {newly_converted} newly converted, {deleted} originals deleted, {updated_files} markdown files updated.")
