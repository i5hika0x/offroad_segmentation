import cv2
import numpy as np
import os
import argparse
from pathlib import Path

IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp']


def main():
    parser = argparse.ArgumentParser(description="Colorize grayscale segmentation masks")
    parser.add_argument('--input_folder', type=str, required=True, help='Folder containing mask images')
    parser.add_argument('--output_folder', type=str, default='', help='Output folder (default: <input>/colorized)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for deterministic colors')
    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder or os.path.join(input_folder, 'colorized')

    if not os.path.isdir(input_folder):
        raise FileNotFoundError(f"Input folder not found: {input_folder}")

    os.makedirs(output_folder, exist_ok=True)

    image_files = [
        f for f in Path(input_folder).iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]

    print(f"Found {len(image_files)} image files to process")

    rng = np.random.default_rng(args.seed)
    color_map = {}

    for image_file in sorted(image_files):
        print(f"Processing: {image_file.name}")

        im = cv2.imread(str(image_file), cv2.IMREAD_UNCHANGED)

        if im is None:
            print(f"  Skipped: Could not read {image_file.name}")
            continue

        if im.ndim == 3:
            im = im[:, :, 0]

        unique_values = np.unique(im)
        im2 = np.zeros((im.shape[0], im.shape[1], 3), dtype=np.uint8)

        for v in unique_values:
            key = int(v)
            if key not in color_map:
                color_map[key] = rng.integers(0, 255, (3,), dtype=np.uint8)
            im2[im == v] = color_map[key]

        output_path = os.path.join(output_folder, f"{image_file.stem}.png")
        cv2.imwrite(output_path, im2)
        print(f"  Saved: {output_path}")

    print(f"\nProcessing complete! Colorized images saved to: {output_folder}")
    print(f"Total unique values found: {len(color_map)}")


if __name__ == '__main__':
    main()