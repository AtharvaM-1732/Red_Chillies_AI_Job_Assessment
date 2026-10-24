# Assessment 1 — AI-Based Image Processing with ComfyUI

## 1. Project Overview

This project demonstrates AI-based image processing using ComfyUI and a pretrained Stable Diffusion XL checkpoint.

    All models used for performing the tasks are "open-source" models.

The assessment covers two image-processing tasks:

- **Output 1 — Background Extension and Upscaling:** Extend missing background regions and increase the image resolution.
- **Output 2 — Object Removal and Addition:** Remove an existing object from an image and add a new object using inpainting.

The workflow uses a node-based pipeline, allowing the image-processing steps to be executed and inspected visually.

## 2. Project Structure

```text
assessment-1-image-processing/
├── README.md
├── workflows/
│   └── assessment1_workflow.json
├── outputs/
│   ├── branch_a_outpainted.png
│   ├── branch_a_upscaled.png
│   ├── branch_b_object_removed.png
│   └── branch_b_object_added.png
├── input/
│   ├── branch_a_input.jpg
│   ├── branch_b_input.jpeg
│   └── .gitkeep
├── docs/
│   └── workflow-guide.md
├── requirements.txt
└── .gitignore
```

The filenames above describe the recommended structure. Replace them with the actual generated files before submitting the repository.

## 3. Technology Stack

- ComfyUI — node-based image-generation workflow
- Stable Diffusion XL checkpoint: `Raymnants.3.0-sdxl.safetensors`
- VAE encoding and decoding
- KSampler for diffusion-based image generation
- VAE Encode for Inpainting for mask-based editing
- ImagePadForOutpaint for background extension
- ImageUpscaleWithModel for image upscaling

## 4. Installation

### 1. Install ComfyUI

Install ComfyUI by following its official installation instructions:

https://github.com/comfyanonymous/ComfyUI

### 2. Download the model

Place the checkpoint file in:

```text
ComfyUI/models/checkpoints/
```

Required checkpoint:

```text
Raymnants.3.0-sdxl.safetensors
```

For Branch A, place the required upscaling model in:

```text
ComfyUI/models/upscale_models/
```

The current workflow references:

```text
1x-ITF-SkinDiffDetail-Lite-v1.pth
```

**Note:** This is a 1× model and does not increase image dimensions. Replace it with a suitable upscaling model if a higher-resolution output is required.

### 3. Load the workflow

1. Start ComfyUI.
2. Open the ComfyUI workflow editor.
3. Load `workflows/assessment1_workflow.json`.
4. Upload the input images when prompted.
5. Verify that all model files and node connections are available.
6. Execute each branch and save the resulting images.

## 5. Workflow Description

### Branch A — Background Extension and Upscaling

The first branch extends the image canvas and generates the missing background.

Pipeline:

```text
Load Image
    ↓
ImagePadForOutpaint
    ↓
VAE Encode for Inpainting
    ↓
KSampler
    ↓
VAE Decode
    ↓
Image Upscaling
    ↓
Save Image
```

The current padding settings add 160 pixels to the left and 160 pixels to the right, with no additional padding at the top or bottom.

The outpainting prompt encourages the model to continue the existing scenery while maintaining consistent lighting, colors, textures, and visual details.

---

### Branch B — Object Removal and Addition

The second branch uses a two-stage inpainting workflow.

**Stage 1: Object removal**

The input image is encoded with an inpainting mask. The diffusion model reconstructs the masked region using a background-focused prompt.

**Stage 2: Object addition**

The output of Stage 1 is passed to another inpainting stage. A positive prompt describes the new object, while a negative prompt discourages common visual artifacts.

For this workflow, the target object is a realistic bicycle.

Pipeline:

```text
Load Image + Mask
        ↓
VAE Encode for Inpainting
        ↓
KSampler — Stage 1
        ↓
VAE Decode
        ↓
VAE Encode for Inpainting
        ↓
KSampler — Stage 2
        ↓
VAE Decode
        ↓
Save Image
```

The object placement depends on the inpainting mask. The intended region must be masked correctly for reliable object insertion or removal.

## 6. Image Preprocessing

The workflow uses the following preprocessing operations:

- Load the source image into ComfyUI.
- Extend the canvas for Branch A using image padding.
- Generate an inpainting mask for the region that needs modification.
- Encode the image and mask into latent space using the checkpoint's VAE.
- Use text prompts to guide image reconstruction and object generation.
- Decode the generated latent representation back into an image.

The current Branch B workflow connects the MASK output of the Load Image node to both inpainting stages. Verify that the loaded image provides the intended mask. If not, create or edit the mask in ComfyUI before running the workflow.

## 7. Model and Sampling Configuration

The current workflow uses the following settings.

| Parameter | Branch A | Branch B — Stage 1 | Branch B — Stage 2 |
|---|---:|---:|---:|
| Checkpoint | SDXL checkpoint | SDXL checkpoint | SDXL checkpoint |
| Sampling steps | 25 | 25 | 25 |
| CFG scale | 5.5 | 5.5 | 8 |
| Sampler | DPM++ 2M | DPM++ 2M | DPM++ 2M |
| Scheduler | Karras | Karras | Karras |
| Denoise | 1.0 | 1.0 | 1.0 |

The workflow uses a pretrained checkpoint for inference. No separate model training or fine-tuning is included.

## 8. Installation Requirements

ComfyUI manages the model execution and dependencies. No separate Python inference script is required for the current node-based implementation.

Example `requirements.txt`:

```text
# Image generation is executed through ComfyUI.
# Install ComfyUI and its dependencies using the official instructions.
# No additional Python packages are required by this repository
# unless custom scripts are added.
```

## 9. Running the Workflow

1. Open the workflow JSON in ComfyUI.
2. Confirm the checkpoint and upscaling model are installed.
3. Select the appropriate input image.
4. Create or verify the inpainting mask for Branch B.
5. Run Branch A to generate the extended image.
6. Run Branch B to generate the object-edited image.
7. Save the generated outputs to the `outputs/` directory.
8. Check the image dimensions, orientation, format, and visual quality.

## 10. Prediction Instructions

This project performs image generation and editing rather than conventional classification or regression prediction.

To process a new image:

1. Load the image into the appropriate Load Image node.
2. Adjust the mask and padding according to the task.
3. Update the text prompts if the target object or scene changes.
4. Execute the relevant workflow branch.
5. Save and inspect the output image.

## 11. Evaluation Results

The assessment requires landscape images with a minimum resolution of 720 pixels.

Record the actual results after running the workflow.

| Output | Operation | Resolution | Format | Status |
|---|---|---|---|---|
| Output 1 (branch_a_upscaled_1680x768.png) | Background extension and upscaling | 1680 x 768 | PNG | ✅ Completed |
| Output 2 (branch_b_object_added_1672x936.png)| Object removal and addition | 1672 x 936 | PNG | ✅ Completed |

Evaluation should include:

- Resolution and landscape orientation
- Successful extension of missing background regions
- Successful removal of the target object
- Successful insertion of the requested object
- Consistency of perspective, lighting, shadows, and textures
- Visible artifacts, blurred areas, or unnatural boundaries

No quantitative quality metrics are reported because verified output images and evaluation measurements have not yet been documented.

## 12. Known Limitations

- Generated content may contain artifacts, distorted details, or inconsistent textures.
- Object insertion quality depends on the prompt, mask size, and placement.
- An incorrect or empty mask can prevent the expected inpainting result.
- The current 1× upscaling model does not increase resolution.
- Results can vary between runs when the sampling seed is randomized.
- Large images may require additional GPU memory and processing time.
- The workflow uses a pretrained checkpoint and does not include a separate training pipeline.

## 13. Deliverables

The final repository should contain:

- ✅ README documentation
- ✅ ComfyUI workflow JSON
- ✅ Original input image or an appropriate source reference
- ✅ Generated Output 1
- ✅ Generated Output 2
- ✅ Verified image dimensions and file formats
- ✅ Screenshots of the completed workflow, if useful

## 14. License and Model Attribution

ComfyUI and the selected checkpoint are third-party components. Review their respective licenses and usage terms before redistribution or commercial use.

ComfyUI: https://github.com/comfyanonymous/ComfyUI

