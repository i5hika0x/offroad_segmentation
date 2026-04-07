"""
Prepare RUGD data for this repository.

This script:
1) Matches image/mask files by stem
2) Splits data by sequence (or randomly)
3) Writes this structure:
   output_root/
     train/Color_Images, train/Segmentation
     val/Color_Images, val/Segmentation
     test/Color_Images, test/Segmentation
"""

import argparse
import json
import random
import shutil
from pathlib import Path


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def index_files(folder: Path):
    files = {}
    for path in folder.iterdir():
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            files[path.stem] = path
    return files


def infer_sequence_id(stem: str) -> str:
    # Example: trail-11_02156 -> trail-11
    if "_" in stem:
        prefix, suffix = stem.rsplit("_", 1)
        if suffix.isdigit():
            return prefix
    return stem


def split_sequences(stems, train_ratio, val_ratio, seed, mode):
    if mode == "random":
        rng = random.Random(seed)
        shuffled = list(stems)
        rng.shuffle(shuffled)

        n_total = len(shuffled)
        n_train = max(1, int(n_total * train_ratio))
        n_val = max(1, int(n_total * val_ratio))
        if n_train + n_val >= n_total:
            n_val = max(1, n_total - n_train - 1)

        train_items = set(shuffled[:n_train])
        val_items = set(shuffled[n_train:n_train + n_val])
        test_items = set(shuffled[n_train + n_val:])
        return train_items, val_items, test_items

    groups = {}
    for stem in stems:
        seq = infer_sequence_id(stem)
        groups.setdefault(seq, []).append(stem)

    seq_ids = sorted(groups.keys())
    rng = random.Random(seed)
    rng.shuffle(seq_ids)

    n_seq = len(seq_ids)
    n_train_seq = max(1, int(n_seq * train_ratio))
    n_val_seq = max(1, int(n_seq * val_ratio))
    if n_train_seq + n_val_seq >= n_seq:
        n_val_seq = max(1, n_seq - n_train_seq - 1)

    train_seq = set(seq_ids[:n_train_seq])
    val_seq = set(seq_ids[n_train_seq:n_train_seq + n_val_seq])
    test_seq = set(seq_ids[n_train_seq + n_val_seq:])

    train_items, val_items, test_items = set(), set(), set()
    for seq, seq_stems in groups.items():
        if seq in train_seq:
            train_items.update(seq_stems)
        elif seq in val_seq:
            val_items.update(seq_stems)
        else:
            test_items.update(seq_stems)

    return train_items, val_items, test_items


def ensure_dirs(output_root: Path):
    for split in ["train", "val", "test"]:
        (output_root / split / "Color_Images").mkdir(parents=True, exist_ok=True)
        (output_root / split / "Segmentation").mkdir(parents=True, exist_ok=True)


def copy_pair(stem, image_map, mask_map, output_root, split_name):
    src_image = image_map[stem]
    src_mask = mask_map[stem]

    dst_image = output_root / split_name / "Color_Images" / src_image.name
    dst_mask = output_root / split_name / "Segmentation" / src_mask.name

    shutil.copy2(src_image, dst_image)
    shutil.copy2(src_mask, dst_mask)


def main():
    parser = argparse.ArgumentParser(description="Prepare RUGD data for training in this repo")
    parser.add_argument("--images_dir", required=True, help="Folder containing raw RGB frames")
    parser.add_argument("--masks_dir", required=True, help="Folder containing segmentation masks")
    parser.add_argument("--output_root", default="rugd_ready", help="Output folder for split dataset")
    parser.add_argument("--train_ratio", type=float, default=0.64)
    parser.add_argument("--val_ratio", type=float, default=0.10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--split_mode", choices=["by-sequence", "random"], default="by-sequence")
    args = parser.parse_args()

    images_dir = Path(args.images_dir)
    masks_dir = Path(args.masks_dir)
    output_root = Path(args.output_root)

    if not images_dir.exists():
        raise FileNotFoundError(f"images_dir not found: {images_dir}")
    if not masks_dir.exists():
        raise FileNotFoundError(f"masks_dir not found: {masks_dir}")

    image_map = index_files(images_dir)
    mask_map = index_files(masks_dir)

    common = sorted(set(image_map.keys()) & set(mask_map.keys()))
    if not common:
        raise RuntimeError("No matching image/mask stems found. Check input folders.")

    split_mode = "random" if args.split_mode == "random" else "sequence"
    train_items, val_items, test_items = split_sequences(
        common,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        seed=args.seed,
        mode=split_mode,
    )

    ensure_dirs(output_root)

    for stem in train_items:
        copy_pair(stem, image_map, mask_map, output_root, "train")
    for stem in val_items:
        copy_pair(stem, image_map, mask_map, output_root, "val")
    for stem in test_items:
        copy_pair(stem, image_map, mask_map, output_root, "test")

    summary = {
        "total_pairs": len(common),
        "train": len(train_items),
        "val": len(val_items),
        "test": len(test_items),
        "split_mode": args.split_mode,
        "seed": args.seed,
        "train_ratio": args.train_ratio,
        "val_ratio": args.val_ratio,
        "test_ratio": round(1.0 - args.train_ratio - args.val_ratio, 6),
    }

    summary_path = output_root / "split_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("RUGD dataset preparation complete")
    print(json.dumps(summary, indent=2))
    print(f"Saved summary to: {summary_path}")


if __name__ == "__main__":
    main()
