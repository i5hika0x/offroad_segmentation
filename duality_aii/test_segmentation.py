"""
Segmentation evaluation script for Falcon desert hackathon dataset.

Outputs:
- Mean IoU, Dice, pixel accuracy
- Per-class IoU and Dice table
- Saved predicted masks and overlays
- Failure-case CSV and JSON summary
"""

import argparse
import csv
import json
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
IGNORE_INDEX = 255

DEFAULT_VALUE_MAP = {
    100: 0,   # Trees
    200: 1,   # Lush Bushes
    300: 2,   # Dry Grass
    500: 3,   # Dry Bushes
    550: 4,   # Ground Clutter
    600: 5,   # Flowers
    700: 6,   # Logs
    800: 7,   # Rocks
    7100: 8,  # Landscape
    10000: 9, # Sky
}

DEFAULT_CLASS_NAMES = [
    "Trees",
    "Lush Bushes",
    "Dry Grass",
    "Dry Bushes",
    "Ground Clutter",
    "Flowers",
    "Logs",
    "Rocks",
    "Landscape",
    "Sky",
]

value_map = DEFAULT_VALUE_MAP.copy()
mapping_mode = "int"
n_classes = (max(value_map.values()) + 1) if value_map else 0
class_names = DEFAULT_CLASS_NAMES.copy()


def _ensure_contiguous_mapping(parsed: dict) -> None:
    values = sorted(set(parsed.values()))
    expected = list(range(len(values)))
    if values != expected:
        raise ValueError(
            "Mapping class IDs must be contiguous and start at 0. "
            f"Found IDs: {values}"
        )


def load_value_map(mapping_json_path: str):
    with open(mapping_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    mode = data.get("mode", "int")
    raw_mapping = data.get("mapping", {})
    parsed = {}

    if mode == "rgb":
        for key, value in raw_mapping.items():
            rgb = tuple(int(x) for x in str(key).split(","))
            if len(rgb) != 3:
                raise ValueError(f"Invalid RGB key in mapping: {key}")
            parsed[rgb] = int(value)
    else:
        for key, value in raw_mapping.items():
            parsed[int(key)] = int(value)

    if not parsed:
        raise ValueError("Loaded mapping is empty")

    _ensure_contiguous_mapping(parsed)
    return parsed, mode


def infer_class_names_from_map(current_map: dict) -> list:
    if all(isinstance(k, int) for k in current_map.keys()):
        if set(current_map.keys()) == set(DEFAULT_VALUE_MAP.keys()):
            return DEFAULT_CLASS_NAMES.copy()
    return [f"Class_{idx}" for idx in range(max(current_map.values()) + 1)]


def set_value_map(new_map, mode):
    global value_map, mapping_mode, n_classes, class_names
    value_map = new_map
    mapping_mode = mode
    n_classes = (max(value_map.values()) + 1) if value_map else 0
    class_names = infer_class_names_from_map(value_map)


def convert_mask(mask: Image.Image) -> Image.Image:
    arr = np.array(mask)

    if mapping_mode == "rgb":
        if arr.ndim == 2:
            arr = np.stack([arr, arr, arr], axis=-1)
        if arr.shape[2] > 3:
            arr = arr[:, :, :3]

        new_arr = np.full(arr.shape[:2], IGNORE_INDEX, dtype=np.uint8)
        for raw_value, new_value in value_map.items():
            rgb = np.array(raw_value, dtype=arr.dtype)
            new_arr[np.all(arr == rgb, axis=-1)] = new_value
    else:
        if arr.ndim == 3:
            arr = arr[:, :, 0]
        new_arr = np.full(arr.shape, IGNORE_INDEX, dtype=np.uint8)
        for raw_value, new_value in value_map.items():
            new_arr[arr == raw_value] = new_value

    return Image.fromarray(new_arr)


def build_color_palette(num_classes: int) -> np.ndarray:
    base = np.array(
        [
            [34, 139, 34],
            [0, 200, 70],
            [210, 180, 140],
            [139, 90, 43],
            [120, 120, 20],
            [255, 120, 180],
            [139, 69, 19],
            [128, 128, 128],
            [160, 82, 45],
            [135, 206, 235],
        ],
        dtype=np.uint8,
    )

    if num_classes <= len(base):
        return base[:num_classes]

    rng = np.random.default_rng(42)
    extra = rng.integers(0, 255, size=(num_classes - len(base), 3), dtype=np.uint8)
    return np.vstack([base, extra])


def mask_to_color(mask: np.ndarray, color_palette: np.ndarray) -> np.ndarray:
    color_mask = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
    for class_id in range(len(color_palette)):
        color_mask[mask == class_id] = color_palette[class_id]
    return color_mask


def denormalize_image(img_tensor: torch.Tensor) -> np.ndarray:
    arr = img_tensor.detach().cpu().numpy().transpose(1, 2, 0)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    arr = (arr * std + mean) * 255.0
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return arr


class MaskDataset(Dataset):
    def __init__(self, data_dir, image_transform, mask_resize):
        root = Path(data_dir)
        self.image_dir = root / "Color_Images"
        self.mask_dir = root / "Segmentation"
        self.image_transform = image_transform
        self.mask_resize = mask_resize

        if not self.image_dir.exists():
            raise FileNotFoundError(f"Missing folder: {self.image_dir}")
        if not self.mask_dir.exists():
            raise FileNotFoundError(f"Missing folder: {self.mask_dir}")

        image_names = {
            p.name for p in self.image_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS
        }
        mask_names = {
            p.name for p in self.mask_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS
        }
        self.data_ids = sorted(image_names & mask_names)

        if not self.data_ids:
            raise RuntimeError(f"No matching image/mask file names in {root}")

    def __len__(self):
        return len(self.data_ids)

    def __getitem__(self, idx):
        name = self.data_ids[idx]
        image = Image.open(self.image_dir / name).convert("RGB")
        mask = Image.open(self.mask_dir / name)
        mask = convert_mask(mask)

        image = self.image_transform(image)
        mask = self.mask_resize(mask)
        mask_arr = np.array(mask, dtype=np.uint8)
        mask_tensor = torch.from_numpy(mask_arr.astype(np.int64))
        return image, mask_tensor, name


class SegmentationHeadConvNeXt(nn.Module):
    def __init__(self, in_channels, out_channels, token_w, token_h):
        super().__init__()
        self.h = token_h
        self.w = token_w

        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, 128, kernel_size=7, padding=3),
            nn.GELU(),
        )

        self.block = nn.Sequential(
            nn.Conv2d(128, 128, kernel_size=7, padding=3, groups=128),
            nn.GELU(),
            nn.Conv2d(128, 128, kernel_size=1),
            nn.GELU(),
        )

        self.classifier = nn.Conv2d(128, out_channels, kernel_size=1)

    def forward(self, x):
        bsz, n_tokens, channels = x.shape
        x = x.reshape(bsz, self.h, self.w, channels).permute(0, 3, 1, 2)
        x = self.stem(x)
        x = self.block(x)
        return self.classifier(x)


def update_confusion_matrix(conf_mat, pred, target, num_classes, ignore_index):
    valid = target != ignore_index
    if valid.sum() == 0:
        return conf_mat

    pred = pred[valid]
    target = target[valid]
    idx = target * num_classes + pred
    bins = torch.bincount(idx, minlength=num_classes * num_classes)
    conf_mat += bins.reshape(num_classes, num_classes).cpu().numpy().astype(np.int64)
    return conf_mat


def metrics_from_confusion(conf_mat):
    conf = conf_mat.astype(np.float64)
    tp = np.diag(conf)
    fp = conf.sum(axis=0) - tp
    fn = conf.sum(axis=1) - tp
    union = tp + fp + fn

    iou = np.divide(tp, union, out=np.full_like(tp, np.nan), where=union > 0)
    dice_den = (2.0 * tp) + fp + fn
    dice = np.divide(2.0 * tp, dice_den, out=np.full_like(tp, np.nan), where=dice_den > 0)

    total = conf.sum()
    pixel_acc = float(tp.sum() / total) if total > 0 else 0.0

    return {
        "mean_iou": float(np.nanmean(iou)),
        "mean_dice": float(np.nanmean(dice)),
        "pixel_acc": pixel_acc,
        "per_class_iou": iou.tolist(),
        "per_class_dice": dice.tolist(),
    }


def compute_sample_iou(pred: np.ndarray, target: np.ndarray, num_classes: int) -> float:
    valid = target != IGNORE_INDEX
    if not np.any(valid):
        return float("nan")

    pred = pred[valid]
    target = target[valid]

    ious = []
    for class_id in range(num_classes):
        p = pred == class_id
        t = target == class_id
        union = np.logical_or(p, t).sum()
        if union == 0:
            continue
        inter = np.logical_and(p, t).sum()
        ious.append(inter / union)

    return float(np.mean(ious)) if ious else float("nan")


def parse_args():
    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(description="Evaluate segmentation model")
    parser.add_argument("--model_path", type=str, default=str(script_dir / "segmentation_head.pth"))
    parser.add_argument(
        "--data_dir",
        type=str,
        default=str(script_dir / ".." / "Offroad_Segmentation_testImages"),
    )
    parser.add_argument("--output_dir", type=str, default="./predictions")
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--num_workers", type=int, default=0)
    parser.add_argument("--save_predictions", type=int, default=1, choices=[0, 1])
    parser.add_argument("--failure_k", type=int, default=20)
    parser.add_argument("--mapping_json", type=str, default="")
    parser.add_argument(
        "--backbone_size",
        type=str,
        default="small",
        choices=["small", "base", "large", "giant"],
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.mapping_json:
        loaded_map, loaded_mode = load_value_map(args.mapping_json)
        set_value_map(loaded_map, loaded_mode)
        print(f"Loaded mapping from {args.mapping_json} | mode={mapping_mode} | classes={n_classes}")
    else:
        print(f"Using default Falcon mapping | mode={mapping_mode} | classes={n_classes}")

    output_dir = Path(args.output_dir)
    pred_mask_dir = output_dir / "pred_masks"
    overlay_dir = output_dir / "overlays"
    output_dir.mkdir(parents=True, exist_ok=True)
    if bool(args.save_predictions):
        pred_mask_dir.mkdir(parents=True, exist_ok=True)
        overlay_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    w = int(((960 / 2) // 14) * 14)
    h = int(((540 / 2) // 14) * 14)

    image_transform = transforms.Compose([
        transforms.Resize((h, w)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    mask_resize = transforms.Resize((h, w), interpolation=transforms.InterpolationMode.NEAREST)

    dataset = MaskDataset(args.data_dir, image_transform=image_transform, mask_resize=mask_resize)
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=(device.type == "cuda"),
    )

    print(f"Evaluation samples: {len(dataset)}")

    backbone_archs = {
        "small": "vits14",
        "base": "vitb14_reg",
        "large": "vitl14_reg",
        "giant": "vitg14_reg",
    }
    backbone_name = f"dinov2_{backbone_archs[args.backbone_size]}"
    backbone = torch.hub.load("facebookresearch/dinov2", backbone_name)
    backbone.to(device).eval()

    state = torch.load(args.model_path, map_location=device)
    if "classifier.weight" not in state:
        raise ValueError("Checkpoint is not a segmentation head state_dict.")
    out_channels = int(state["classifier.weight"].shape[0])

    if out_channels != n_classes:
        class_names_local = [f"Class_{i}" for i in range(out_channels)]
        num_eval_classes = out_channels
    else:
        class_names_local = class_names
        num_eval_classes = n_classes

    sample_img, _, _ = dataset[0]
    with torch.no_grad():
        emb = backbone.forward_features(sample_img.unsqueeze(0).to(device))["x_norm_patchtokens"]
    n_embed = emb.shape[2]

    classifier = SegmentationHeadConvNeXt(
        in_channels=n_embed,
        out_channels=out_channels,
        token_w=w // 14,
        token_h=h // 14,
    ).to(device)
    classifier.load_state_dict(state)
    classifier.eval()

    color_palette = build_color_palette(num_eval_classes)
    conf_mat = np.zeros((num_eval_classes, num_eval_classes), dtype=np.int64)
    sample_records = []

    with torch.no_grad():
        for imgs, labels, names in tqdm(loader, desc="Evaluating"):
            imgs = imgs.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            feats = backbone.forward_features(imgs)["x_norm_patchtokens"]
            logits = classifier(feats)
            logits = F.interpolate(logits, size=imgs.shape[2:], mode="bilinear", align_corners=False)
            preds = torch.argmax(logits, dim=1)

            update_confusion_matrix(
                conf_mat,
                pred=preds.detach().cpu(),
                target=labels.detach().cpu(),
                num_classes=num_eval_classes,
                ignore_index=IGNORE_INDEX,
            )

            for idx, name in enumerate(names):
                pred_np = preds[idx].detach().cpu().numpy().astype(np.uint8)
                gt_np = labels[idx].detach().cpu().numpy().astype(np.uint8)
                sample_iou = compute_sample_iou(pred_np, gt_np, num_eval_classes)

                sample_records.append(
                    {
                        "image": str(name),
                        "sample_mean_iou": sample_iou,
                    }
                )

                if bool(args.save_predictions):
                    rgb = denormalize_image(imgs[idx])
                    color_mask = mask_to_color(pred_np, color_palette)
                    overlay = cv2.addWeighted(rgb, 0.6, color_mask, 0.4, 0.0)

                    cv2.imwrite(str(pred_mask_dir / str(name)), color_mask[:, :, ::-1])
                    cv2.imwrite(str(overlay_dir / str(name)), overlay[:, :, ::-1])

    metrics = metrics_from_confusion(conf_mat)

    per_class_rows = []
    for class_id in range(num_eval_classes):
        per_class_rows.append(
            {
                "class_id": class_id,
                "class_name": class_names_local[class_id],
                "iou": metrics["per_class_iou"][class_id],
                "dice": metrics["per_class_dice"][class_id],
            }
        )

    sample_records_sorted = sorted(
        sample_records,
        key=lambda x: (float("inf") if np.isnan(x["sample_mean_iou"]) else x["sample_mean_iou"]),
    )
    worst_samples = sample_records_sorted[: max(0, args.failure_k)]

    with (output_dir / "per_class_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["class_id", "class_name", "iou", "dice"])
        writer.writeheader()
        writer.writerows(per_class_rows)

    with (output_dir / "failure_cases.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "sample_mean_iou"])
        writer.writeheader()
        writer.writerows(worst_samples)

    summary = {
        "mean_iou": metrics["mean_iou"],
        "mean_dice": metrics["mean_dice"],
        "pixel_accuracy": metrics["pixel_acc"],
        "num_samples": len(dataset),
        "class_names": class_names_local,
        "per_class": per_class_rows,
        "worst_samples": worst_samples,
        "pred_masks_dir": str(pred_mask_dir) if bool(args.save_predictions) else "disabled",
        "overlay_dir": str(overlay_dir) if bool(args.save_predictions) else "disabled",
    }

    with (output_dir / "evaluation_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n===== FINAL RESULTS =====")
    print(f"Mean IoU      : {metrics['mean_iou']:.4f}")
    print(f"Mean Dice     : {metrics['mean_dice']:.4f}")
    print(f"Pixel Accuracy: {metrics['pixel_acc']:.4f}")
    print(f"Saved summary : {output_dir / 'evaluation_summary.json'}")
    print(f"Saved class CSV: {output_dir / 'per_class_metrics.csv'}")
    print(f"Saved failure CSV: {output_dir / 'failure_cases.csv'}")


if __name__ == "__main__":
    main()
