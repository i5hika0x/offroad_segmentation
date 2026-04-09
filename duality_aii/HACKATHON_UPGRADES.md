# Hackathon Upgrade Checklist (Falcon Desert Segmentation)

This document lists the upgrades applied to this repository for the current Falcon desert segmentation workflow, without changing dataset source.

## 1) Model Training Upgrades

Implemented in `train_segmentation.py`:

- Corrected default class mapping to include `Flowers (600)` and align with Falcon classes.
- Unknown/unmapped mask pixels now use `ignore_index=255` instead of silently becoming class 0.
- Added paired augmentations for train data (image and mask stay aligned):
  - horizontal flip
  - vertical flip (optional)
  - color jitter
- Added class imbalance handling:
  - `--class_weighting auto` computes class weights from train masks
- Added optimizer and scheduler controls:
  - `--optimizer adamw|sgd`
  - `--scheduler cosine|none`
- Added mixed precision option:
  - `--amp 1` for faster CUDA training
- Added early stopping:
  - `--early_stop_patience`
- Added richer artifacts:
  - `history.csv`, `history.json`, `training_curves.png`
  - `training_summary.json`
  - best/last checkpoints in `checkpoints/`
  - best checkpoint auto-exported to `segmentation_head.pth`
  - class names exported to `class_names.json`

## 2) Evaluation + Reporting Upgrades

Implemented in `test_segmentation.py`:

- Same Falcon mapping logic and unknown-label handling as training.
- Computes global metrics for judging/reporting:
  - Mean IoU
  - Mean Dice
  - Pixel Accuracy
- Exports per-class metrics:
  - `per_class_metrics.csv`
- Exports failure-case list:
  - `failure_cases.csv` (worst sample IoU)
- Saves visual evidence for report/presentation:
  - predicted color masks in `pred_masks/`
  - overlay images in `overlays/`
- Exports full summary:
  - `evaluation_summary.json`

## 3) Frontend Consistency Upgrade

Implemented in `app.py`:

- Updated default class labels to match Falcon class list (includes Flowers).
- Updated default visualization palette to match training/evaluation class order.

## 4) Recommended Commands (Current Dataset)

Train:

```bash
python train_segmentation.py --train_dir "<dataset_root>/train" --val_dir "<dataset_root>/val" --mapping_json "<dataset_root>/mask_mapping.json" --output_dir "<dataset_root>/train_stats" --batch_size 2 --epochs 20 --lr 3e-4 --num_workers 0 --backbone_size small --optimizer adamw --scheduler cosine --class_weighting auto --amp 1 --early_stop_patience 8 --aug_hflip 0.5 --aug_color_jitter 0.2
```

Evaluate:

```bash
python test_segmentation.py --model_path "segmentation_head.pth" --data_dir "<dataset_root>/test" --mapping_json "<dataset_root>/mask_mapping.json" --output_dir "<dataset_root>/predictions" --batch_size 2 --num_workers 0 --save_predictions 1 --failure_k 20
```

## 5) Deliverable Mapping

- Trained model package:
  - `segmentation_head.pth`
  - `train_segmentation.py`
  - `test_segmentation.py`
  - `class_names.json`
- Performance evaluation:
  - IoU/Dice/Pixel Accuracy in `evaluation_summary.json`
  - Loss and trend plots in `training_curves.png`
  - Failure-case analysis in `failure_cases.csv` + overlays
