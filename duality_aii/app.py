import io
import json
import os
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image

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


def resolve_class_names(class_names_path: str, num_classes: int):
    """Load class names from JSON file if provided, else generate defaults."""
    if class_names_path and os.path.exists(class_names_path):
        with open(class_names_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            loaded = [str(x) for x in data]
        elif isinstance(data, dict):
            loaded = [str(data.get(str(i), f"Class_{i}")) for i in range(num_classes)]
        else:
            loaded = []

        if len(loaded) == num_classes:
            return loaded

    if num_classes == len(DEFAULT_CLASS_NAMES):
        return DEFAULT_CLASS_NAMES
    return [f"Class_{i}" for i in range(num_classes)]


class SegmentationHeadConvNeXt(nn.Module):
    def __init__(self, in_channels, out_channels, token_w, token_h):
        super().__init__()
        self.H, self.W = token_h, token_w

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

        self.classifier = nn.Conv2d(128, out_channels, 1)

    def forward(self, x):
        bsz, n_tokens, channels = x.shape
        x = x.reshape(bsz, self.H, self.W, channels).permute(0, 3, 1, 2)
        x = self.stem(x)
        x = self.block(x)
        return self.classifier(x)


def mask_to_color(mask: np.ndarray, color_palette: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    color_mask = np.zeros((h, w, 3), dtype=np.uint8)
    for class_id in range(len(color_palette)):
        color_mask[mask == class_id] = color_palette[class_id]
    return color_mask


def overlay_mask(rgb: np.ndarray, color_mask: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    return cv2.addWeighted(rgb, 1.0 - alpha, color_mask, alpha, 0.0)


@st.cache_resource
def load_models(checkpoint_path: str, device: str):
    backbone = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14").to(device).eval()

    state = torch.load(checkpoint_path, map_location=device)
    if "classifier.weight" not in state:
        raise ValueError("Checkpoint missing classifier.weight. Expected segmentation head state dict.")
    out_channels = int(state["classifier.weight"].shape[0])

    # Use the same token geometry as training script defaults
    w = int(((960 / 2) // 14) * 14)
    h = int(((540 / 2) // 14) * 14)

    # Infer embedding size from a dummy tensor
    dummy = torch.zeros(1, 3, h, w).to(device)
    with torch.no_grad():
        embed = backbone.forward_features(dummy)["x_norm_patchtokens"]
    n_embed = embed.shape[2]

    head = SegmentationHeadConvNeXt(
        in_channels=n_embed,
        out_channels=out_channels,
        token_w=w // 14,
        token_h=h // 14,
    ).to(device)

    head.load_state_dict(state)
    head.eval()

    return backbone, head, h, w, out_channels


def preprocess(image: Image.Image, h: int, w: int) -> torch.Tensor:
    transform = transforms.Compose(
        [
            transforms.Resize((h, w)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    return transform(image).unsqueeze(0)


def predict(backbone, head, image: Image.Image, device: str, h: int, w: int, class_names, color_palette):
    original = np.array(image.convert("RGB"))
    tensor = preprocess(image, h, w).to(device)

    with torch.no_grad():
        feats = backbone.forward_features(tensor)["x_norm_patchtokens"]
        logits = head(feats)
        logits = F.interpolate(logits, size=(h, w), mode="bilinear", align_corners=False)
        pred = torch.argmax(logits, dim=1).squeeze(0).cpu().numpy().astype(np.uint8)

    color_mask = mask_to_color(pred, color_palette)

    # Resize mask back to original size for display
    color_mask_resized = cv2.resize(
        color_mask,
        (original.shape[1], original.shape[0]),
        interpolation=cv2.INTER_NEAREST,
    )
    overlay = overlay_mask(original, color_mask_resized)

    coverage = []
    total_pixels = pred.size
    for class_id, class_name in enumerate(class_names):
        ratio = float((pred == class_id).sum()) / float(total_pixels)
        coverage.append((class_name, ratio * 100.0))

    return original, color_mask_resized, overlay, coverage


def main():
    st.set_page_config(page_title="Offroad Segmentation Demo", layout="wide")
    st.title("Offroad Semantic Segmentation Demo")
    st.caption("DINOv2 + segmentation head inference UI")

    with st.sidebar:
        st.header("Configuration")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        st.write(f"Device: {device}")

        checkpoint_default = str(Path(__file__).parent / "segmentation_head.pth")
        checkpoint_path = st.text_input("Checkpoint Path", value=checkpoint_default)

        class_names_default = str(Path(__file__).parent / "class_names.json")
        class_names_path = st.text_input("Class Names JSON (optional)", value=class_names_default)

        alpha = st.slider("Overlay Opacity", min_value=0.1, max_value=0.9, value=0.45, step=0.05)

    if not os.path.exists(checkpoint_path):
        st.warning("Checkpoint not found. Train first or provide a valid checkpoint path.")
        st.stop()

    try:
        backbone, head, h, w, out_channels = load_models(checkpoint_path, device)
    except Exception as exc:
        st.error(f"Failed to load model/checkpoint: {exc}")
        st.stop()

    class_names = resolve_class_names(class_names_path, out_channels)
    color_palette = build_color_palette(len(class_names))

    with st.sidebar:
        st.markdown("---")
        st.write("Loaded classes")
        for idx, name in enumerate(class_names):
            st.write(f"{idx}: {name}")

    uploaded = st.file_uploader("Upload one RGB image", type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"])

    if uploaded is None:
        st.info("Upload an image to run inference.")
        return

    try:
        image = Image.open(io.BytesIO(uploaded.read())).convert("RGB")
    except Exception as exc:
        st.error(f"Failed to parse image: {exc}")
        st.stop()

    original, color_mask, overlay, coverage = predict(
        backbone,
        head,
        image,
        device,
        h,
        w,
        class_names,
        color_palette,
    )
    overlay = overlay_mask(original, color_mask, alpha=alpha)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Original")
        st.image(original, use_container_width=True)
    with col2:
        st.subheader("Predicted Mask")
        st.image(color_mask, use_container_width=True)
    with col3:
        st.subheader("Overlay")
        st.image(overlay, use_container_width=True)

    st.subheader("Class Coverage (%)")
    cov_data = {"Class": [c[0] for c in coverage], "Coverage": [round(c[1], 2) for c in coverage]}
    st.dataframe(cov_data, use_container_width=True)


if __name__ == "__main__":
    main()
