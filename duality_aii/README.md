# Offroad Semantic Segmentation (DINOv2)

This repository contains a complete offroad semantic segmentation pipeline:

- dataset preparation for RUGD-style image/mask folders
- training with a frozen DINOv2 backbone and segmentation head
- evaluation on test split
- Streamlit frontend for interactive inference

## Falcon Desert Hackathon Notes

If your team already downloaded the Falcon desert dataset, keep using that same dataset and folder layout. You do not need a different dataset.

Expected split structure:

- `<dataset_root>/train/Color_Images`
- `<dataset_root>/train/Segmentation`
- `<dataset_root>/val/Color_Images`
- `<dataset_root>/val/Segmentation`
- `<dataset_root>/test/Color_Images`
- `<dataset_root>/test/Segmentation`

Default Falcon class mapping used by upgraded scripts:

- `100 -> Trees`
- `200 -> Lush Bushes`
- `300 -> Dry Grass`
- `500 -> Dry Bushes`
- `550 -> Ground Clutter`
- `600 -> Flowers`
- `700 -> Logs`
- `800 -> Rocks`
- `7100 -> Landscape`
- `10000 -> Sky`

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

Use your own segmentation dataset (Falcon or custom).

If your dataset is already split, keep this structure and skip to training/evaluation:

- `<dataset_root>/train/Color_Images`
- `<dataset_root>/train/Segmentation`
- `<dataset_root>/val/Color_Images`
- `<dataset_root>/val/Segmentation`
- `<dataset_root>/test/Color_Images`
- `<dataset_root>/test/Segmentation`

If you have raw image/mask folders, continue with Step 5 to generate train/val/test splits.

## 5) Prepare Train/Val/Test Folder Structure

Run:

```bash
python prepare_rugd_dataset.py --images_dir "<images_dir>" --masks_dir "<masks_dir>" --output_root "<output_root>" --split_mode by-sequence --train_ratio 0.64 --val_ratio 0.10 --seed 42
```

Example:

```bash
python prepare_rugd_dataset.py --images_dir "<falcon_images_dir>" --masks_dir "<falcon_masks_dir>" --output_root "<dataset_root>" --split_mode by-sequence --train_ratio 0.64 --val_ratio 0.10 --seed 42
```

If your data is already split into train/val/test folders, you can skip this step.

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

Generic command:

```bash
python train_segmentation.py --train_dir "<output_root>/train" --val_dir "<output_root>/val" --mapping_json "<output_root>/mask_mapping.json" --output_dir "<output_root>/train_stats" --batch_size 2 --epochs 20 --lr 3e-4 --num_workers 0 --backbone_size small --optimizer adamw --scheduler cosine --class_weighting auto --amp 1 --early_stop_patience 8 --aug_hflip 0.5 --aug_color_jitter 0.2
```

Training saves artifacts in `<output_root>/train_stats`:

- `checkpoints/best_segmentation_head.pth`
- `checkpoints/last_segmentation_head.pth`
- `history.csv`, `history.json`, `training_curves.png`
- `training_summary.json`
- `class_names.json`

And exports best checkpoint in repo root as:

- `segmentation_head.pth`

For a quick smoke test, use `--epochs 1 --batch_size 1`.

## 8) Evaluate

Generic command:

```bash
python test_segmentation.py --model_path "segmentation_head.pth" --data_dir "<output_root>/test" --mapping_json "<output_root>/mask_mapping.json" --output_dir "<output_root>/predictions" --batch_size 2 --num_workers 0 --save_predictions 1 --failure_k 20
```

You will get metrics and reporting artifacts:

- Mean IoU, Mean Dice, Pixel Accuracy
- `evaluation_summary.json`
- `per_class_metrics.csv`
- `failure_cases.csv`
- `pred_masks/` and `overlays/` for visual report evidence

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


