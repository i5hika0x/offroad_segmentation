# Offroad Semantic Segmentation (DINOv2)

This repository contains a complete offroad semantic segmentation pipeline:

- dataset preparation for RUGD-style image/mask folders
- training with a frozen DINOv2 backbone and segmentation head
- evaluation on test split
- Streamlit frontend for interactive inference

The guide below is for a person cloning this repository on a fresh machine.

## 1) Clone The Repository

```bash
git clone https://github.com/Abhrxdip/duality_ai.git
cd duality_ai
```

If you cloned a different remote, the rest of the commands are the same.

## 2) Create And Activate Python Environment

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS/Linux (bash/zsh)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3) Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install torch torchvision opencv-contrib-python numpy pillow tqdm matplotlib streamlit
```

## 4) Choose Dataset Source

You have two options.

### Option A: Small Demo Dataset (Fast, recommended for first run)

- Download: http://rugd.vision/data/RUGD_sample-data.zip

After extracting, you should have folders like:

- `<sample_root>/images`
- `<sample_root>/annotations`

### Option B: Full RUGD Dataset

- Raw frames: http://rugd.vision/data/RUGD_frames-with-annotations.zip
- Annotations: http://rugd.vision/data/RUGD_annotations.zip
- Dataset info: https://datasetninja.com/rugd

After extracting, identify:

- `images_dir` (RGB frames)
- `masks_dir` (segmentation masks)

## 5) Prepare Train/Val/Test Folder Structure

Run:

```bash
python prepare_rugd_dataset.py --images_dir "<images_dir>" --masks_dir "<masks_dir>" --output_root "<output_root>" --split_mode by-sequence --train_ratio 0.64 --val_ratio 0.10 --seed 42
```

Example:

```bash
python prepare_rugd_dataset.py --images_dir "demo_data/rugd_sample/RUGD_sample-data/images" --masks_dir "demo_data/rugd_sample/RUGD_sample-data/annotations" --output_root "demo_data/rugd_demo_ready" --split_mode by-sequence --train_ratio 0.64 --val_ratio 0.10 --seed 42
```

This creates:

- `<output_root>/train/Color_Images`
- `<output_root>/train/Segmentation`
- `<output_root>/val/Color_Images`
- `<output_root>/val/Segmentation`
- `<output_root>/test/Color_Images`
- `<output_root>/test/Segmentation`

## 6) Generate Mask Mapping

RUGD masks can be RGB-coded. Generate class mapping JSON:

```bash
python generate_mask_mapping.py --mask_dir "<output_root>/train/Segmentation" --output_json "<output_root>/mask_mapping.json"
```

## 7) Train

```bash
python train_segmentation.py --train_dir "<output_root>/train" --val_dir "<output_root>/val" --mapping_json "<output_root>/mask_mapping.json" --output_dir "<output_root>/train_stats" --batch_size 2 --epochs 10 --lr 1e-4 --num_workers 0 --backbone_size small
```

Training saves checkpoint in repo root as:

- `segmentation_head.pth`

For a quick smoke test, use `--epochs 1 --batch_size 1`.

## 8) Evaluate

```bash
python test_segmentation.py --model_path "segmentation_head.pth" --data_dir "<output_root>/test" --mapping_json "<output_root>/mask_mapping.json" --output_dir "<output_root>/predictions" --batch_size 2 --num_workers 0
```

You will get metrics such as Mean IoU, Dice, Pixel Accuracy, and mAP@0.5.

## 9) Run Frontend Demo

```bash
python -m streamlit run app.py
```

In the app:

- checkpoint path should point to `segmentation_head.pth`
- upload RGB image files only (from `Color_Images` or original `images` folder)
- do not upload annotation masks

## 10) Repository Scripts

- `train_segmentation.py`: training pipeline
- `test_segmentation.py`: evaluation + prediction export
- `app.py`: Streamlit inference UI
- `prepare_rugd_dataset.py`: split and format data
- `generate_mask_mapping.py`: build class-id mapping JSON
- `visualize.py`: mask colorization utility
- `RUGD_FROM_SCRATCH.md`: additional beginner walkthrough

## 11) Common Issues

- `FileNotFoundError ... Color_Images`
  - Check the `--train_dir`, `--val_dir`, and `--data_dir` values.
- Frontend says checkpoint missing
  - Train first or set correct checkpoint path in sidebar.
- Poor performance on CPU
  - Use fewer epochs, batch size 1, and smaller experiments for demo.

## Team

- Team Name: Code Squad
- Hackathon Track: Semantic Segmentation - Offroad Autonomy
