"""Batch convert PNG/JPG images to WebP and update markdown references."""
import os
import re
from pathlib import Path
from PIL import Image

DOCS_DIR = Path(__file__).parent / "docs"
SKIP_DIRS = {"img"}  # skip docs/img (theme assets: logo, favicon)
EXTENSIONS = {".png", ".jpg", ".jpeg"}
QUALITY = 85

# Step 1: Find and convert all images
converted = []
for img_path in DOCS_DIR.rglob("*"):
    if not img_path.is_file():
        continue
    if img_path.suffix.lower() not in EXTENSIONS:
        continue
    # Skip theme assets directly in docs/img/
    rel_parts = img_path.relative_to(DOCS_DIR).parts
    if len(rel_parts) >= 2 and rel_parts[0] == "img":
        continue

    webp_path = img_path.with_suffix(".webp")
    if webp_path.exists():
        print(f"SKIP (already exists): {webp_path}")
        continue

    print(f"Converting: {img_path.relative_to(DOCS_DIR)}", end=" ... ")
    try:
        img = Image.open(img_path)
        # Preserve RGBA mode for transparency
        if img.mode in ("RGBA", "LA", "P"):
            img.save(webp_path, "WEBP", quality=QUALITY, method=6)
        else:
            img = img.convert("RGB")
            img.save(webp_path, "WEBP", quality=QUALITY, method=6)

        old_kb = img_path.stat().st_size / 1024
        new_kb = webp_path.stat().st_size / 1024
        ratio = (1 - new_kb / old_kb) * 100
        print(f"{old_kb:.0f}KB -> {new_kb:.0f}KB ({ratio:.0f}% smaller)")
        converted.append((img_path, webp_path))
    except Exception as e:
        print(f"ERROR: {e}")
        continue

# Step 2: Update all .md files
print(f"\nUpdating markdown references...")
updated_files = 0
for md_path in DOCS_DIR.rglob("*.md"):
    content = md_path.read_text(encoding="utf-8")
    new_content = content
    for old_path, new_path in converted:
        # Get relative paths from the markdown file's directory
        old_rel = os.path.relpath(old_path, md_path.parent).replace("\\", "/")
        new_rel = os.path.relpath(new_path, md_path.parent).replace("\\", "/")
        new_content = new_content.replace(old_rel, new_rel)
        # Also handle the case where the extension is written differently
        new_content = re.sub(
            re.escape(old_path.stem) + r"\.(png|jpg|jpeg)",
            new_path.stem + ".webp",
            new_content
        )

    if new_content != content:
        md_path.write_text(new_content, encoding="utf-8")
        updated_files += 1
        print(f"  Updated: {md_path.relative_to(DOCS_DIR)}")

# Step 3: Delete original files
print(f"\nDeleting original files...")
for old_path, _ in converted:
    old_path.unlink()
    print(f"  Deleted: {old_path.relative_to(DOCS_DIR)}")

print(f"\nDone! Converted {len(converted)} images, updated {updated_files} markdown files.")
