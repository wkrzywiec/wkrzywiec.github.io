#!/usr/bin/env python3
"""
Resize PNG and JPG images so the longest edge matches MAX_EDGE_PX.
Resized copies are saved to OUTPUT_DIR, preserving the original filenames.

Configuration
-------------
Adjust the three constants below before running the script.
"""

from pathlib import Path
from PIL import Image

# ── Configuration ────────────────────────────────────────────────────────────

# Directory that contains the source images (absolute or relative to CWD)
INPUT_DIR = Path("./images")

# Directory where resized copies will be written (created if it does not exist)
OUTPUT_DIR = Path("resized")

# The longest edge of the resized image, in pixels
MAX_EDGE_PX = 1400

# ─────────────────────────────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def resize_image(src: Path, dst: Path, max_edge: int) -> None:
    with Image.open(src) as img:
        original_size = img.size  # (width, height)
        longest = max(original_size)

        if longest <= max_edge:
            print(f"  skip  {src.name}  ({original_size[0]}x{original_size[1]} – already within limit)")
            img.save(dst)
            return

        scale = max_edge / longest
        new_size = (round(original_size[0] * scale), round(original_size[1] * scale))
        resized = img.resize(new_size, Image.LANCZOS)
        resized.save(dst)
        print(f"  done  {src.name}  ({original_size[0]}x{original_size[1]} → {new_size[0]}x{new_size[1]})")


def main() -> None:
    input_path = INPUT_DIR.resolve()
    output_path = OUTPUT_DIR.resolve()

    if not input_path.is_dir():
        raise SystemExit(f"ERROR: INPUT_DIR does not exist: {input_path}")

    output_path.mkdir(parents=True, exist_ok=True)

    images = [
        f for f in input_path.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not images:
        print(f"No PNG/JPG images found in {input_path}")
        return

    print(f"Processing {len(images)} image(s)  →  max edge: {MAX_EDGE_PX}px")
    print(f"Output folder: {output_path}\n")

    for src in sorted(images):
        dst = output_path / src.name
        try:
            resize_image(src, dst, MAX_EDGE_PX)
        except Exception as exc:
            print(f"  ERROR {src.name}: {exc}")

    print("\nDone.")


if __name__ == "__main__":
    main()
