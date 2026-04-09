"""
ML Wrapper Module - Offroad Semantic Segmentation
This module provides a clean interface for model inference, isolated from the backend.
Can be reused by any backend (FastAPI, Flask, or future civic backend).

Author: Duality AI
Purpose: Plug-and-play inference module for segmentation predictions
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image


# ============================================================================
# CONFIG & CONSTANTS
# ============================================================================

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

DEFAULT_COLOR_PALETTE = np.array([
    [34, 139, 34],      # Trees - Dark Green
    [0, 200, 70],       # Lush Bushes - Bright Green
    [210, 180, 140],    # Dry Grass - Tan
    [139, 90, 43],      # Dry Bushes - Brown
    [120, 120, 20],     # Ground Clutter - Olive
    [255, 120, 180],    # Flowers - Pink
    [139, 69, 19],      # Logs - Saddle Brown
    [128, 128, 128],    # Rocks - Gray
    [160, 82, 45],      # Landscape - Sienna
    [135, 206, 235],    # Sky - Sky Blue
], dtype=np.uint8)


# ============================================================================
# SEGMENTATION HEAD ARCHITECTURE
# ============================================================================

class SegmentationHeadConvNeXt(nn.Module):
    """
    ConvNeXt-based segmentation head for DINOv2 features.
    Processes patch tokens and upsamples to full resolution predictions.
    """
    def __init__(self, in_channels: int, out_channels: int, token_w: int, token_h: int):
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

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        bsz, n_tokens, channels = x.shape
        x = x.reshape(bsz, self.H, self.W, channels).permute(0, 3, 1, 2)
        x = self.stem(x)
        x = self.block(x)
        return self.classifier(x)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def build_color_palette(num_classes: int) -> np.ndarray:
    """Build color palette for visualization."""
    if num_classes <= len(DEFAULT_COLOR_PALETTE):
        return DEFAULT_COLOR_PALETTE[:num_classes]

    rng = np.random.default_rng(42)
    extra = rng.integers(0, 255, size=(num_classes - len(DEFAULT_COLOR_PALETTE), 3), dtype=np.uint8)
    return np.vstack([DEFAULT_COLOR_PALETTE, extra])


def resolve_class_names(class_names_path: Optional[str], num_classes: int) -> List[str]:
    """Load class names from JSON file if provided, else use defaults."""
    if class_names_path and os.path.exists(class_names_path):
        try:
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
        except Exception as e:
            print(f"Warning: Failed to load class names from {class_names_path}: {e}")

    if num_classes == len(DEFAULT_CLASS_NAMES):
        return DEFAULT_CLASS_NAMES
    return [f"Class_{i}" for i in range(num_classes)]


def mask_to_color(mask: np.ndarray, color_palette: np.ndarray) -> np.ndarray:
    """Convert class mask to RGB color visualization."""
    h, w = mask.shape
    color_mask = np.zeros((h, w, 3), dtype=np.uint8)
    for class_id in range(len(color_palette)):
        color_mask[mask == class_id] = color_palette[class_id]
    return color_mask


def overlay_mask(rgb: np.ndarray, color_mask: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    """Blend color mask with original RGB image."""
    return cv2.addWeighted(rgb, 1.0 - alpha, color_mask, alpha, 0.0)


# ============================================================================
# MODEL LOADER
# ============================================================================

class SegmentationModel:
    """
    Wrapper for DINOv2 + ConvNeXt segmentation model.
    Manages model loading, preprocessing, and inference.
    
    Can be used standalone or integrated into any backend.
    """
    
    def __init__(
        self,
        checkpoint_path: str,
        class_names_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize model.
        
        Args:
            checkpoint_path: Path to saved segmentation head checkpoint
            class_names_path: Optional path to JSON file with class names
            device: Device to load model on ('cuda' or 'cpu'). 
                   Auto-detects if None.
        
        Raises:
            FileNotFoundError: If checkpoint doesn't exist
            ValueError: If checkpoint format is invalid
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.checkpoint_path = checkpoint_path
        
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        
        # Load backbone
        self.backbone = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14").to(self.device).eval()
        
        # Load segmentation head
        state = torch.load(checkpoint_path, map_location=self.device)
        if "classifier.weight" not in state:
            raise ValueError("Checkpoint missing classifier.weight. Expected segmentation head state dict.")
        
        self.out_channels = int(state["classifier.weight"].shape[0])
        
        # Compute token geometry (must match training)
        self.h = int(((960 / 2) // 14) * 14)
        self.w = int(((960 / 2) // 14) * 14)
        
        # Infer embedding dimension
        dummy = torch.zeros(1, 3, self.h, self.w).to(self.device)
        with torch.no_grad():
            embed = self.backbone.forward_features(dummy)["x_norm_patchtokens"]
        n_embed = embed.shape[2]
        
        self.head = SegmentationHeadConvNeXt(
            in_channels=n_embed,
            out_channels=self.out_channels,
            token_w=self.w // 14,
            token_h=self.h // 14,
        ).to(self.device)
        
        self.head.load_state_dict(state)
        self.head.eval()
        
        # Load class names and color palette
        self.class_names = resolve_class_names(class_names_path, self.out_channels)
        self.color_palette = build_color_palette(self.out_channels)
    
    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image for model input."""
        transform = transforms.Compose([
            transforms.Resize((self.h, self.w)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        return transform(image).unsqueeze(0)
    
    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """
        Run inference on image.
        
        Args:
            image: PIL Image (RGB or RGBA)
        
        Returns:
            {
                "mask": np.ndarray (h, w) - class indices,
                "color_mask": np.ndarray (h, w, 3) - RGB visualization,
                "overlay": np.ndarray (h, w, 3) - blended with original,
                "coverage": List[(class_name, percentage), ...],
                "class_distribution": {class_name: percentage, ...}
            }
        """
        # Convert to RGB if needed
        original = np.array(image.convert("RGB"))
        
        # Preprocess
        tensor = self.preprocess(image).to(self.device)
        
        # Inference
        with torch.no_grad():
            feats = self.backbone.forward_features(tensor)["x_norm_patchtokens"]
            logits = self.head(feats)
            logits = F.interpolate(logits, size=(self.h, self.w), mode="bilinear", align_corners=False)
            pred = torch.argmax(logits, dim=1).squeeze(0).cpu().numpy().astype(np.uint8)
        
        # Generate visualizations
        color_mask = mask_to_color(pred, self.color_palette)
        color_mask_resized = cv2.resize(
            color_mask,
            (original.shape[1], original.shape[0]),
            interpolation=cv2.INTER_NEAREST,
        )
        overlay = overlay_mask(original, color_mask_resized)
        
        # Compute class coverage statistics
        coverage = []
        class_dist = {}
        total_pixels = pred.size
        
        for class_id, class_name in enumerate(self.class_names):
            ratio = float((pred == class_id).sum()) / float(total_pixels)
            percentage = ratio * 100.0
            coverage.append((class_name, percentage))
            class_dist[class_name] = percentage
        
        return {
            "mask": pred,
            "color_mask": color_mask_resized,
            "overlay": overlay,
            "coverage": coverage,
            "class_distribution": class_dist,
        }
    
    @staticmethod
    def image_to_base64(image: np.ndarray) -> str:
        """Convert numpy image to base64 string for JSON serialization."""
        import base64
        _, buffer = cv2.imencode('.png', image)
        return base64.b64encode(buffer).decode('utf-8')
    
    @staticmethod
    def save_results(output_dir: str, prefix: str, results: Dict[str, Any], original_image: np.ndarray):
        """Save prediction results to disk."""
        os.makedirs(output_dir, exist_ok=True)
        
        cv2.imwrite(os.path.join(output_dir, f"{prefix}_original.png"), cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR))
        cv2.imwrite(os.path.join(output_dir, f"{prefix}_mask.png"), results["color_mask"])
        cv2.imwrite(os.path.join(output_dir, f"{prefix}_overlay.png"), cv2.cvtColor(results["overlay"], cv2.COLOR_RGB2BGR))


# ============================================================================
# MAIN INFERENCE FUNCTION
# ============================================================================

def predict(
    image: Image.Image,
    model: SegmentationModel,
    return_visualizations: bool = True,
) -> Dict[str, Any]:
    """
    High-level prediction function for easy integration.
    
    Args:
        image: PIL Image to predict
        model: Loaded SegmentationModel instance
        return_visualizations: If True, include color_mask and overlay in response
    
    Returns:
        Structured prediction output (see SegmentationModel.predict)
    """
    result = model.predict(image)
    
    if not return_visualizations:
        result.pop("color_mask", None)
        result.pop("overlay", None)
    
    return result


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: How to use this module
    checkpoint_path = Path(__file__).parent / "segmentation_head.pth"
    class_names_path = Path(__file__).parent / "class_names.json"
    
    # Initialize model (done once at startup)
    model = SegmentationModel(
        checkpoint_path=str(checkpoint_path),
        class_names_path=str(class_names_path) if class_names_path.exists() else None,
        device="cuda",
    )
    
    # Run inference on an image
    image = Image.open("test_image.jpg")
    result = predict(image, model)
    
    print("Prediction successful!")
    print(f"Class distribution: {result['class_distribution']}")
