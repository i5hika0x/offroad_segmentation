# Frontend: Offroad Segmentation Demo

This frontend is a Streamlit app that runs semantic segmentation inference using
`segmentation_head.pth` and a DINOv2 backbone.

## Features
- Upload a single RGB image
- View original image, predicted mask, and overlay
- Adjustable overlay opacity
- Per-class pixel coverage table
- Works with dynamic class count from checkpoint (not fixed to 10 classes)

## Run
From repository root:

```bash
c:/Users/abhra/OneDrive/Desktop/Offroad_Segmentation_Scripts/.venv/Scripts/python.exe -m pip install -r requirements_frontend.txt
c:/Users/abhra/OneDrive/Desktop/Offroad_Segmentation_Scripts/.venv/Scripts/python.exe -m streamlit run app.py
```

## Notes
- Default checkpoint path is `segmentation_head.pth` in repo root.
- If checkpoint is missing, app will warn and stop.
- First run may be slower because DINOv2 is loaded from torch hub.
- Optional: provide a `class_names.json` file in repo root for readable class labels.
	- JSON list format example: `["class0", "class1", "class2"]`
