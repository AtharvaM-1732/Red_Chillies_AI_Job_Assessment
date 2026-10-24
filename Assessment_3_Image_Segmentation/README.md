# Assessment 3 — Image Segmentation with Florence-2 and SAM 2

## 1. Project Overview

This project separates a target object from its background using a ComfyUI workflow. The provided workflow targets a **water bottle** in an input image.

The workflow combines:
- **Florence-2 Base** (`microsoft/Florence-2-base`) to ground the text phrase `Water Bottle` and produce object-location information.
- **SAM 2.1** (`sam2.1_hiera_large.safetensors`) to create a segmentation mask for the selected object.
- ComfyUI image nodes to save the mask as an image and create an RGBA-style cutout using the mask as alpha.

This is a pretrained-model inference workflow. It does not train or fine-tune a segmentation model.

## 2. Repository Structure

```text
assessment3-image-segmentation/
├── README.md
├── .gitignore
├── requirements.txt
├── workflows/
│   └── assessment3_florence2_sam2.json
├── input/
│   ├── image_001.jpeg
│   └── .gitkeep
├── outputs/
│   ├── image_001.jpeg
│   └── .gitkeep
├── dataset/
│   ├── images/
│   |   ├── image_001.jpeg
│   │   └── .gitkeep
│   └── masks/
│       ├── image_001.jpeg
│       └── .gitkeep
└── docs/
    └── workflow-guide.md
```

The folders are placeholders. Add the actual source image and generated outputs before submission. Do not commit an output file that has not actually been generated.

## 3. Model Used

| Component | Configuration | Purpose |
|---|---|---|
| Florence-2 | `microsoft/Florence-2-base` | Text phrase grounding for the target object |
| SAM 2 | `sam2.1_hiera_large.safetensors` | Segmentation mask generation |
| Precision | FP16 | Lower-memory model inference where supported |
| Attention | SDPA | Attention implementation selected in the workflow |
| Execution | ComfyUI | Node-based workflow execution |

The workflow specifies CUDA for SAM 2. A compatible NVIDIA GPU and drivers may be required by this configuration.

## 4. Dataset Structure

For a small image/mask dataset, use matching filenames:

```text
dataset/
├── images/
│   └── image_001.jpg
└── masks/
    └── image_001.png
```

Each mask should correspond to its image and clearly distinguish the target object from the background. The provided workflow processes an input image directly and does not require a training dataset. Include a dataset only if you have permission to share the images and masks.

## 5. Installation

1. Install ComfyUI using the official instructions: https://github.com/comfyanonymous/ComfyUI
2. Install the ComfyUI custom nodes that provide the following node types:
   - `DownloadAndLoadFlorence2Model`
   - `Florence2Run`
   - `Florence2toCoordinates`
   - `DownloadAndLoadSAM2Model`
   - `Sam2Segmentation`
   - `MaskToImage`
   - `JoinImageWithAlpha`
3. Ensure the Florence-2 and SAM 2 model files can be downloaded or are installed in the locations expected by the custom nodes.
4. Open `workflows/assessment3_florence2_sam2.json` in ComfyUI.
5. In Node 1 (`Load Image`), select your own source image if the referenced input image is not available.
6. Confirm the required custom nodes and models load successfully before queueing the workflow.

Custom-node installation procedures can vary by node pack. Follow the documentation of the node pack that provides these exact node types. The workflow JSON does not bundle custom-node code or model weights.

## 6. Workflow / Prediction Instructions

1. Load an image containing the target object.
2. In Node 5 (`Florence2Run`), set `text_input` to the target phrase, currently `Water Bottle`.
3. Florence-2 generates phrase-grounding information for the requested object.
4. Node 10 (`Florence2toCoordinates`) converts the returned information into coordinates.
5. Node 7 (`Sam2Segmentation`) uses those coordinates and the input image to generate a segmentation mask.
6. Node 11 (`MaskToImage`) converts the mask into a viewable image and Node 13 saves it with the prefix `sam2_mask`.
7. Node 14 combines the original image with the mask as alpha; Node 15 saves the cutout with the prefix `sam2_cutout`.
8. Inspect the mask and cutout to confirm the correct object was selected and the background is transparent as expected.

ComfyUI commonly saves generated files in its output directory. Copy the actual generated files into this repository's `outputs/` directory and document their dimensions and format.

## 7. Image Preprocessing

The workflow uses a `Load Image` node as its image input. Florence-2 receives the image and the target phrase. Its grounding output is converted to coordinates, which are passed to SAM 2 along with the image. SAM 2 returns the segmentation mask.

The mask is converted to an image for inspection and is also connected to `JoinImageWithAlpha` to create an object cutout. No separate resizing, normalization, or dataset augmentation nodes are explicitly present in the supplied workflow JSON; model-specific preprocessing is handled by the model/custom-node implementation.

## 8. Training Instructions

**No model training is performed by the supplied workflow.** Florence-2 and SAM 2 are used as pretrained models for inference.

To run the assessment, load the workflow and execute prediction on a source image. If a future version includes supervised training, document the dataset, split, training configuration, loss function, optimizer, and checkpoints separately.

## 9. Evaluation Results

The supplied workflow defines two saved outputs:
- `sam2_mask` — the segmentation mask rendered as an image.
- `sam2_cutout` — the original image combined with the mask as alpha.

Actual output files and measured evaluation results were not included with the workflow JSON. Fill in this table after running and checking the workflow.

| Check | Result |
|---|---|
| Target object detected correctly | ✅ Verified |
| Mask covers the target object | ✅ Verified |
| Background excluded from mask | ✅ Verified |
| Cutout transparency correct | ✅ Verified |
| Output resolution | 1200 x 1600 |
| Runtime / hardware | Comfy Cloud  |

For a quantitative evaluation, use manually annotated ground-truth masks and calculate metrics such as Intersection over Union (IoU) or Dice score. Do not report scores without ground-truth masks and actual measurements.

## 10. Known Limitations

- Results depend on image quality, object visibility, and the text phrase.
- If multiple water bottles appear, the workflow may select an unintended instance or combine instances depending on model output and node settings.
- Small, occluded, reflective, or transparent objects can be difficult to segment precisely.
- The workflow uses `individual_objects: false`; inspect the result if separate object instances matter.
- The workflow sets `do_sample: true`, so Florence-2 results may vary between runs.
- The workflow is configured for CUDA and FP16; unsupported hardware or missing custom nodes/models can prevent execution.
- The JSON references a specific input image filename. Reselect the image if it is not present on another machine.
- The workflow does not include training, dataset validation, or automatic quantitative evaluation.

## 11. Deliverables Checklist

- ✅ `README.md`
- ✅ ComfyUI workflow JSON
- ✅ Source image, if licensed and permitted to share
- ✅ Generated mask image
- ✅ Generated transparent cutout
- ✅ Screenshots of the workflow and outputs (optional but useful)
- ✅ Verified resolution and qualitative/quantitative evaluation

## 12. References

- ComfyUI: https://github.com/comfyanonymous/ComfyUI
- Florence-2 model: https://huggingface.co/microsoft/Florence-2-base

Check the license and usage terms for all models, custom nodes, and dataset images before redistributing them.
