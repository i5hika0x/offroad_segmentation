# RUGD From Scratch (Beginner Guide)

This guide helps you run the full project even if you are new to ML.

## 1) What You Need

- Windows machine
- Internet connection
- Python environment in this repo (`.venv`)
- RUGD dataset files (images + masks)

## 2) Install Python Packages

Run from repo root:

```powershell
c:/Users/abhra/OneDrive/Desktop/Offroad_Segmentation_Scripts/.venv/Scripts/python.exe -m pip install torch torchvision opencv-contrib-python tqdm matplotlib streamlit pillow
```

## 3) Download RUGD Dataset

You said to use Dataset Ninja source:

- Dataset page: https://datasetninja.com/rugd
- Original links are listed there, including:
  - Raw frames zip
  - Annotations zip

Alternative official source links shown on that page include:

- http://rugd.vision/data/RUGD_frames-with-annotations.zip
- http://rugd.vision/data/RUGD_annotations.zip

Extract both zips somewhere on your PC.

## 4) Find Your Images and Masks Folders

After extraction, find:

- `images_dir`: folder that has RGB frame images
- `masks_dir`: folder that has segmentation masks with matching filenames

Example (your paths will differ):

- `C:/datasets/RUGD/frames`
- `C:/datasets/RUGD/annotations`

## 5) Prepare Train/Val/Test Split for This Repo

This repo expects:

- `train/Color_Images` and `train/Segmentation`
- `val/Color_Images` and `val/Segmentation`
- `test/Color_Images` and `test/Segmentation`

Use the helper script to create that format:

```powershell
c:/Users/abhra/OneDrive/Desktop/Offroad_Segmentation_Scripts/.venv/Scripts/python.exe prepare_rugd_dataset.py --images_dir "C:/datasets/RUGD/frames" --masks_dir "C:/datasets/RUGD/annotations" --output_root "C:/datasets/rugd_ready" --split_mode by-sequence --train_ratio 0.64 --val_ratio 0.10 --seed 42
```

This creates:

- `C:/datasets/rugd_ready/train/...`
- `C:/datasets/rugd_ready/val/...`
- `C:/datasets/rugd_ready/test/...`

## 6) Generate Mask Mapping (Important)

RUGD masks may not use the same IDs as the original repo dataset. Generate mapping automatically:

```powershell
c:/Users/abhra/OneDrive/Desktop/Offroad_Segmentation_Scripts/.venv/Scripts/python.exe generate_mask_mapping.py --mask_dir "C:/datasets/rugd_ready/train/Segmentation" --output_json "C:/datasets/rugd_ready/mask_mapping.json"
```

## 7) Train the Model

```powershell
c:/Users/abhra/OneDrive/Desktop/Offroad_Segmentation_Scripts/.venv/Scripts/python.exe train_segmentation.py --train_dir "C:/datasets/rugd_ready/train" --val_dir "C:/datasets/rugd_ready/val" --mapping_json "C:/datasets/rugd_ready/mask_mapping.json" --output_dir "C:/datasets/rugd_ready/train_stats" --batch_size 2 --epochs 10 --lr 1e-4 --num_workers 0 --backbone_size small
```

After training, model checkpoint will be saved as:

- `segmentation_head.pth` in repo root

## 8) Evaluate on Test Split

```powershell
c:/Users/abhra/OneDrive/Desktop/Offroad_Segmentation_Scripts/.venv/Scripts/python.exe test_segmentation.py --model_path "C:/Users/abhra/OneDrive/Desktop/Offroad_Segmentation_Scripts/segmentation_head.pth" --data_dir "C:/datasets/rugd_ready/test" --mapping_json "C:/datasets/rugd_ready/mask_mapping.json" --output_dir "C:/datasets/rugd_ready/predictions" --batch_size 2 --num_workers 0
```

You will see metrics like Mean IoU and Pixel Accuracy in terminal.

## 9) Run Frontend Demo

```powershell
c:/Users/abhra/OneDrive/Desktop/Offroad_Segmentation_Scripts/.venv/Scripts/python.exe -m streamlit run app.py
```

In the app:

- Set checkpoint path to `segmentation_head.pth`
- Optionally provide `class_names.json` if you want custom class labels
- Upload image and view predicted mask + overlay

## 10) Optional: Visualize Any Mask Folder

```powershell
c:/Users/abhra/OneDrive/Desktop/Offroad_Segmentation_Scripts/.venv/Scripts/python.exe visualize.py --input_folder "C:/datasets/rugd_ready/test/Segmentation" --output_folder "C:/datasets/rugd_ready/test/Segmentation_colorized" --seed 42
```

## 11) Common Errors and Fixes

- Error: `FileNotFoundError ... Color_Images`
  - Fix: check `--train_dir`, `--val_dir`, `--data_dir` paths.

- Error: checkpoint load mismatch in app
  - Fix: ensure app checkpoint is from this training pipeline.

- Error: labels look wrong
  - Fix: regenerate and pass `--mapping_json` from train masks.

- Very slow training on CPU
  - Fix: reduce epochs and image size, or use a GPU machine.
