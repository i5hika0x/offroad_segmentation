"""
Generate a mapping file for segmentation masks.

Supports:
- Indexed masks (single channel class ids)
- RGB masks (class color -> class id)

Output format:
{
  "mode": "int" | "rgb",
  "num_classes": N,
  "mapping": {
    "0": 0,
    "1": 1,
    ...
  }
}

For RGB mode, keys are "R,G,B".
"""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def is_grayscale(arr: np.ndarray) -> bool:
    if arr.ndim == 2:
        return True
    if arr.ndim == 3 and arr.shape[2] >= 3:
        return np.array_equal(arr[:, :, 0], arr[:, :, 1]) and np.array_equal(arr[:, :, 1], arr[:, :, 2])
    return False


def iter_masks(mask_dir: Path):
    for path in sorted(mask_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            yield path


def main():
    parser = argparse.ArgumentParser(description="Generate class mapping from segmentation masks")
    parser.add_argument("--mask_dir", required=True, help="Folder containing segmentation masks")
    parser.add_argument("--output_json", default="mask_mapping.json", help="Output mapping JSON path")
    parser.add_argument("--max_masks", type=int, default=0, help="Optional limit for quick inspection (0=all)")
    args = parser.parse_args()

    mask_dir = Path(args.mask_dir)
    if not mask_dir.exists():
        raise FileNotFoundError(f"mask_dir not found: {mask_dir}")

    mask_paths = list(iter_masks(mask_dir))
    if not mask_paths:
        raise RuntimeError(f"No mask files found in: {mask_dir}")

    if args.max_masks > 0:
        mask_paths = mask_paths[:args.max_masks]

    first = np.array(Image.open(mask_paths[0]))
    mode = "int" if is_grayscale(first) else "rgb"

    if mode == "int":
        unique_values = set()
        for path in mask_paths:
            arr = np.array(Image.open(path))
            if arr.ndim == 3:
                arr = arr[:, :, 0]
            vals = np.unique(arr)
            unique_values.update(int(v) for v in vals.tolist())

        sorted_vals = sorted(unique_values)
        mapping = {str(v): i for i, v in enumerate(sorted_vals)}

    else:
        unique_colors = set()
        for path in mask_paths:
            arr = np.array(Image.open(path))
            if arr.ndim == 2:
                arr = np.stack([arr, arr, arr], axis=-1)
            if arr.shape[2] > 3:
                arr = arr[:, :, :3]
            flat = arr.reshape(-1, 3)
            uniq = np.unique(flat, axis=0)
            for color in uniq:
                unique_colors.add((int(color[0]), int(color[1]), int(color[2])))

        sorted_colors = sorted(unique_colors)
        mapping = {f"{c[0]},{c[1]},{c[2]}": i for i, c in enumerate(sorted_colors)}

    output = {
        "mode": mode,
        "num_classes": len(mapping),
        "mapping": mapping,
    }

    output_path = Path(args.output_json)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Mode: {mode}")
    print(f"Classes discovered: {len(mapping)}")
    print(f"Saved mapping to: {output_path}")


if __name__ == "__main__":
    main()
